"""
mcpython - a minecraft clone written in python licenced under the MIT-licence 
(https://github.com/mcpython4-coding/core)

Contributors: uuk, xkcdjerry (inactive)

Based on the game of fogleman (https://github.com/fogleman/Minecraft), licenced under the MIT-licence
Original game "minecraft" by Mojang Studios (www.minecraft.net), licenced under the EULA
(https://account.mojang.com/documents/minecraft_eula)
Mod loader inspired by "Minecraft Forge" (https://github.com/MinecraftForge/MinecraftForge) and similar

This project is not official by mojang and does not relate to it.
"""
# Framework for loading and executing java bytecode
# Mainly independent from mcpython's source
# See Runtime.py for a system for executing the bytecode
# See builtin folder for python implementations for java internals
import struct
import types
import typing
from abc import ABC
import copy

U1 = struct.Struct("!B")
U1_S = struct.Struct("!b")
U2 = struct.Struct("!H")
U2_S = struct.Struct("!h")
U4 = struct.Struct("!I")

INT = struct.Struct("!i")
FLOAT = struct.Struct("!f")
LONG = struct.Struct("!q")
DOUBLE = struct.Struct("!d")


def pop_u1(data: bytearray):
    e = data[:1]
    del data[0]
    return U1.unpack(e)[0]


def pop_u2(data: bytearray):
    e = data[:2]
    del data[:2]
    return U2.unpack(e)[0]


def pop_u4(data: bytearray):
    e = data[:4]
    del data[:4]
    return U4.unpack(e)[0]


def pop_sized(size: int, data: bytearray):
    e = data[:size]
    del data[:size]
    return bytes(e)


def pop_struct(s: struct.Struct, data: bytearray):
    return s.unpack(pop_sized(s.size, data))


def warn(text: str):
    print("[JAVA][WARN]", warn)


def info(text: str):
    pass


def get_bytecode_of_class(class_name: str):
    with open("./" + class_name.replace(".", "/") + ".class", mode="rb") as f:
        return f.read()


class JavaVM:
    def __init__(self):
        self.classes: typing.Dict[
            str, typing.Union["AbstractJavaClass", typing.Type]
        ] = {}
        self.lazy_classes = set()

        self.array_helper = JavaArrayManager(self)

    def load_lazy(self):
        while len(self.lazy_classes) > 0:
            self.get_class(self.lazy_classes.pop())

    def init_builtins(self):
        from mcpython.loader.java.builtin.java.lang import Object, Enum, Integer, Boolean
        from mcpython.loader.java.builtin.java.util import ArrayList, HashMap, Map
        from mcpython.loader.java.builtin.java.nio.file import Path, Paths, Files

    def init_bridge(self):
        from mcpython.loader.java.bridge import util
        from mcpython.loader.java.bridge.codec import builder
        from mcpython.loader.java.bridge.event import registries, content
        from mcpython.loader.java.bridge.fml import loading
        from mcpython.loader.java.bridge.lib import google_collect, logging, fastutil, gson
        from mcpython.loader.java.bridge.world import biomes, collection
        from mcpython.loader.java.bridge.misc import containers, potions
        from mcpython.loader.java.bridge.client import rendering

    def get_class(self, name: str) -> "AbstractJavaClass":
        if name.replace(".", "/") in self.classes:
            cls = self.classes[name.replace(".", "/")]
        else:
            cls = self.load_class(name)

        cls.prepare_use()

        return cls

    def get_lazy_class(self, name: str):
        self.lazy_classes.add(name)
        return lambda: self.get_class(name)

    def load_class(self, name: str) -> "AbstractJavaClass":
        if name.startswith("["):
            return self.array_helper.get(name)

        try:
            bytecode = get_bytecode_of_class(name)
        except FileNotFoundError:
            raise RuntimeError(f"class {name} not found!") from None

        info("loading java class '" + name + "'")

        cls = JavaBytecodeClass()
        cls.from_bytes(bytearray(bytecode))

        self.classes[name.replace(".", "/")] = cls

        cls.bake()

        info(f"class load of class '{name}' (internally: '{cls.name}') finished")

        return cls

    def register_native(self, n: typing.Type["NativeClass"]):
        self.classes[n.NAME] = n()

    def get_method_of_nat(self, nat):
        cls = nat[1][1][1]
        name = nat[2][1][1]
        descriptor = nat[2][2][1]
        cls = self.get_class(cls)
        return cls.get_method(name, descriptor)


class AbstractJavaClass:
    def __init__(self):
        self.name: str = None
        self.file_source: str = None
        self.parent = None
        self.interfaces = []

    def get_method(self, name: str, signature: str, inner=False):
        raise NotImplementedError

    def get_static_attribute(self, name: str):
        raise NotImplementedError

    def set_static_attribute(self, name: str, value):
        raise NotImplementedError

    def create_instance(self):
        raise NotImplementedError

    def on_annotate(self, cls, args):
        raise RuntimeError((self, cls, args))

    def get_dynamic_field_keys(self):
        return set()

    def is_subclass_of(self, class_name: str) -> bool:
        raise NotImplementedError

    def prepare_use(self):
        pass


class NativeClass(AbstractJavaClass, ABC):
    NAME = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.NAME is not None:
            vm.register_native(cls)

    def __init__(self):
        super().__init__()
        self.vm = vm
        self.name = self.NAME

        self.exposed_attributes = {}
        self.exposed_methods = {}

        for key, value in self.__class__.__dict__.items():
            if hasattr(value, "native_name"):
                self.exposed_methods.setdefault(
                    (value.native_name, value.native_signature), getattr(self, key)
                )

    def get_method(self, name: str, signature: str, inner=False):
        try:
            return self.exposed_methods[(name, signature)]
        except KeyError:
            m = (
                self.parent.get_method(name, signature, inner=True)
                if self.parent is not None
                else None
            )
            if m is None:
                for interface in self.interfaces:
                    m = interface.get_method(name, signature, inner=True)
                    if m is not None:
                        return m
                if not inner:
                    raise AttributeError((self, name, signature, self.exposed_methods))
                return
            return m

    def get_static_attribute(self, name: str):
        if name not in self.exposed_attributes:
            raise KeyError(self, name)
        return self.exposed_attributes[name]

    def set_static_attribute(self, name: str, value):
        self.exposed_attributes[name] = value

    def create_instance(self):
        return NativeClassInstance(self)

    def __repr__(self):
        return f"NativeClass({self.NAME})"

    def is_subclass_of(self, class_name: str):
        return self.name == class_name


class NativeClassInstance:
    def __init__(self, native_class: "NativeClass"):
        self.native_class = native_class
        self.fields = {}

    def get_method(self, name: str, signature: str):
        return self.native_class.get_method(name, signature)

    def get_class(self):
        return self.native_class

    def __repr__(self):
        return f"NativeClassInstance(of={self.native_class},id={hex(id(self))})"


def native(name: str, signature: str):
    def setup(method):
        method.native_name = name
        method.native_signature = signature
        return method

    return setup


class ArrayBase(NativeClass):
    def __init__(self, depth: int, name: str, base_class: AbstractJavaClass):
        super().__init__()
        self.base_class = base_class
        self.depth = depth
        self.name = name

    def create_instance(self):
        return []

    @native("clone", "()Ljava/lang/Object;")
    def clone(self, instance):
        return instance.copy()


class JavaArrayManager:
    """
    Helper class for working with java arrays of non-standard type (e.g. [Lnet/minecraft/ResourceLocation;)
    It creates the needed array classes and holds them for later reuse
    """

    def __init__(self, vm):
        self.vm = vm

    def get(self, class_text: str):
        depth = class_text.count("[")
        cls_name = class_text[depth:]
        cls = self.vm.get_class(cls_name.removeprefix("L").removesuffix(";"))

        instance = ArrayBase(depth, class_text, cls)

        self.vm.classes[class_text] = instance
        return instance


class AbstractAttributeParser(ABC):
    NAME: str = None

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        raise NotImplementedError


class ConstantValueParser(AbstractAttributeParser):
    def __init__(self):
        self.value = None
        self.field: "JavaField" = None

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        self.value = table.class_file.cp[pop_u2(data)]
        self.field = table.parent

        if self.field.access & 0x0008:
            table.class_file.on_bake.append(self.inject_static)
        # else:
        #     table.class_file.on_instance_creation.append(self.inject_instance)

    def inject_static(self, class_file: "JavaBytecodeClass"):
        class_file.set_static_attribute(self.field.name, self.value)

    def inject_instance(self, class_file: "JavaBytecodeClass", instance):
        instance.set_attribute(self.field.name, self.value)


class CodeParser(AbstractAttributeParser):
    def __init__(self):
        self.class_file: "JavaBytecodeClass" = None
        self.max_stacks = 0
        self.max_locals = 0
        self.code: bytes = None
        self.exception_table = {}
        self.attributes = JavaAttributeTable(self)

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        self.class_file = table.class_file
        self.max_stacks = pop_u2(data)
        self.max_locals = pop_u2(data)
        size = pop_u4(data)
        self.code = pop_sized(size, data)

        for _ in range(pop_u2(data)):
            start, end, handler, catch = (
                pop_u2(data),
                pop_u2(data),
                pop_u2(data),
                pop_u2(data),
            )
            self.exception_table.setdefault(start, []).append((end, handler, catch))

        self.attributes.from_data(table.class_file, data)


class BootstrapMethods(AbstractAttributeParser):
    def __init__(self):
        self.entries = []

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        for _ in range(pop_u2(data)):
            method_ref = table.class_file.cp[pop_u2(data) - 1]
            arguments = [
                table.class_file.cp[pop_u2(data) - 1] for _ in range(pop_u2(data))
            ]
            self.entries.append((method_ref, arguments))


class StackMapTableParser(AbstractAttributeParser):
    def parse(self, table: "JavaAttributeTable", data: bytearray):
        pass  # todo: implement


class ElementValue:
    def __init__(self):
        self.tag = None
        self.data = None

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        self.tag = tag = chr(pop_u1(data))

        if tag in "BCDFIJSZs":
            self.data = decode_cp_constant(table.class_file.cp[pop_u2(data)-1])
        elif tag == "e":
            cls_name = table.class_file.cp[pop_u2(data)-1][1].removeprefix("L").removesuffix(";")
            attr_name = table.class_file.cp[pop_u2(data)-1][1]

            cls = vm.get_class(cls_name)
            self.data = cls.get_static_attribute(attr_name)
        else:
            raise NotImplementedError(tag)

        return self


class RuntimeVisibleAnnotationsParser(AbstractAttributeParser):
    def __init__(self):
        self.annotations = []

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        for _ in range(pop_u2(data)):
            annotation_type = table.class_file.cp[pop_u2(data)-1][1].removeprefix("L").removesuffix(";")

            values = []

            for _ in range(pop_u2(data)):
                name = table.class_file.cp[pop_u2(data)-1][1]
                value = ElementValue().parse(table, data)
                values.append((name, value))

            self.annotations.append((annotation_type, values))

        # print(self.annotations)


class JavaAttributeTable:
    ATTRIBUTES_NEED_PARSING = {
        "ConstantValue",
        "Code",
        "StackMapTable",
        "BootstrapMethods",
        "NestHost",
        "NestMembers",
        "RuntimeVisibleAnnotations",
    }
    ATTRIBUTES_MAY_PARSING = {
        "Exceptions",
        "InnerClasses",
        "EnclosingMethods",
        "Synthetic",
        "Signature",
        "Record",
        "SourceFile",
        "LineNumberTable",
        "LocalVariableTable",
        "LocalVariableTypeTable",
    }

    ATTRIBUTES = {
        "ConstantValue": ConstantValueParser,
        "Code": CodeParser,
        "BootstrapMethods": BootstrapMethods,
        "StackMapTable": StackMapTableParser,
        "RuntimeVisibleAnnotations": RuntimeVisibleAnnotationsParser,
    }

    def __init__(self, parent):
        self.parent = parent
        self.class_file: "JavaBytecodeClass" = None
        self.attributes_unparsed = {}
        self.attributes = {}

    def from_data(self, class_file: "JavaBytecodeClass", data: bytearray):
        self.class_file = class_file

        for _ in range(pop_u2(data)):
            name = class_file.cp[pop_u2(data) - 1][1]
            data_size = pop_u4(data)
            d = pop_sized(data_size, data)
            self.attributes_unparsed.setdefault(name, []).append(d)

        for key in list(self.attributes_unparsed.keys()):
            if key in self.ATTRIBUTES:
                self.attributes.setdefault(key, [])

                for data in self.attributes_unparsed[key]:
                    instance = self.ATTRIBUTES[key]()
                    instance.parse(self, bytearray(data))
                    self.attributes[key].append(instance)

                del self.attributes_unparsed[key]

        keyset = set(self.attributes_unparsed.keys())

        diff_need = self.ATTRIBUTES_NEED_PARSING.intersection(keyset)
        if diff_need:
            raise RuntimeError(
                f"The following attribute(s) could not be parsed (attribute holder: {self.parent}): "
                + ", ".join(diff_need)
            )

        diff_may = self.ATTRIBUTES_MAY_PARSING.intersection(keyset)
        # if diff_may:
            # info("missing attribute parsing for: " + ", ".join(diff_may))

    def __getitem__(self, item):
        return self.attributes[item]


class JavaField:
    def __init__(self):
        self.class_file: "JavaBytecodeClass" = None
        self.name: str = None
        self.descriptor: str = None
        self.access = 0
        self.attributes = JavaAttributeTable(self)

    def from_data(self, class_file: "JavaBytecodeClass", data: bytearray):
        self.class_file = class_file
        self.access = pop_u2(data)
        self.name = class_file.cp[pop_u2(data) - 1][1]
        self.descriptor = class_file.cp[pop_u2(data) - 1][1]
        self.attributes.from_data(class_file, data)

    def __repr__(self):
        return f"JavaField(name='{self.name}',descriptor='{self.descriptor}',access='{bin(self.access)}',class='{self.class_file.name}')"


class JavaMethod:
    def __init__(self):
        self.class_file: "JavaBytecodeClass" = None
        self.name: str = None
        self.signature: str = None
        self.access = 0
        self.attributes = JavaAttributeTable(self)

        self.code_repr = None

    def from_data(self, class_file: "JavaBytecodeClass", data: bytearray):
        self.class_file = class_file
        self.access = pop_u2(data)
        self.name = class_file.cp[pop_u2(data) - 1][1]
        self.signature = class_file.cp[pop_u2(data) - 1][1]
        self.attributes.from_data(class_file, data)

    def __repr__(self):
        return f"JavaMethod(name='{self.name}',signature='{self.signature}',access='{bin(self.access)}',class='{self.class_file.name}')"


class JavaBytecodeClass(AbstractJavaClass):
    def __init__(self):
        super().__init__()
        self.cp: typing.List[typing.Any] = []
        self.access = 0
        self.methods = {}
        self.fields = {}
        self.dynamic_field_keys = set()
        self.static_field_values = {}
        self.attributes = JavaAttributeTable(self)

        self.on_bake = []
        self.on_instance_creation = []

        self.class_init_complete = False

    def from_bytes(self, data: bytearray):
        magic = pop_u4(data)
        assert magic == 0xCAFEBABE, f"magic {magic} is invalid!"

        minor, major = pop_u2(data), pop_u2(data)

        info(
            f"class file version: {major}.{minor} (Java {major-44 if major > 45 else '1.0.2 or 1.1'}"
            f"{' preview features enabled' if major > 56 and minor == 65535 else ''})"
        )

        cp_size = pop_u2(data) - 1
        self.cp += [None] * cp_size
        i = 0
        while i < cp_size:
            j = i
            i += 1

            tag = pop_u1(data)

            if tag in (7, 8, 16, 19, 20):
                d = tag, pop_u2(data)
            elif tag in (9, 10, 11, 12, 17, 18):
                d = tag, pop_u2(data), pop_u2(data)
            elif tag == 3:
                d = tag, pop_struct(INT, data)[0]
            elif tag == 4:
                d = tag, pop_struct(FLOAT, data)[0]
            elif tag == 5:
                d = tag, pop_struct(LONG, data)[0]
                i += 1
            elif tag == 6:
                d = tag, pop_struct(DOUBLE, data)[0]
                i += 1
            elif tag == 1:
                size = pop_u2(data)
                e = pop_sized(size, data)
                d = tag, e.decode("utf-8")
            elif tag == 15:
                d = tag, pop_u1(data), pop_u2(data)
            else:
                raise ValueError(tag)

            self.cp[j] = list(d)

        for i, e in enumerate(self.cp):
            if e is None: continue

            tag = e[0]

            if tag in (7, 9, 10, 11, 8, 12, 16, 19, 20):
                e = e[1:]
                self.cp[i].clear()
                try:
                    self.cp[i] += [tag] + [self.cp[x - 1] for x in e]
                except TypeError:
                    print(tag, e, self.cp)
                    raise

            elif tag in (15, 17, 18):
                self.cp[i] = self.cp[i][:2] + [self.cp[self.cp[i][-1] - 1]]

        self.access |= pop_u2(data)

        self.name = self.cp[pop_u2(data) - 1][1][1]
        self.parent = vm.get_lazy_class(self.cp[pop_u2(data) - 1][1][1])

        self.interfaces += [
            vm.get_lazy_class(self.cp[pop_u2(data) - 1][1][1])
            for _ in range(pop_u2(data))
        ]

        for _ in range(pop_u2(data)):
            field = JavaField()
            field.from_data(self, data)

            self.fields[field.name] = field

            if field.access & 0x0008:
                self.static_field_values[field.name] = None
            else:
                self.dynamic_field_keys.add(field.name)

        for _ in range(pop_u2(data)):
            method = JavaMethod()
            method.from_data(self, data)

            self.methods[(method.name, method.signature)] = method

        self.attributes.from_data(self, data)

    def get_method(self, name: str, signature: str, inner=False):
        des = (name, signature)
        if des in self.methods:
            return self.methods[des]

        m = self.parent().get_method(*des) if self.parent is not None else None
        if m is not None:
            return m

        raise AttributeError(self, des)

    def get_static_attribute(self, name: str):
        if name not in self.static_field_values:
            if self.parent is not None:
                try:
                    return self.parent().get_static_attribute(name)
                except KeyError:
                    pass

        return self.static_field_values[name]

    def set_static_attribute(self, name: str, value):
        self.static_field_values[name] = value

    def bake(self):
        for method in self.on_bake:
            method(self)
        self.on_bake.clear()

        if "RuntimeVisibleAnnotations" in self.attributes.attributes:
            for annotation in self.attributes["RuntimeVisibleAnnotations"]:
                for cls_name, args in annotation.annotations:
                    cls = vm.get_class(cls_name)
                    cls.on_annotate(self, args)

    def create_instance(self):
        return JavaClassInstance(self)

    def __repr__(self):
        return f"JavaBytecodeClass({self.name},access={bin(self.access)},parent={self.parent()},interfaces=[{', '.join(repr(e()) for e in self.interfaces)}])"

    def get_dynamic_field_keys(self):
        return self.dynamic_field_keys | self.parent().get_dynamic_field_keys()

    def is_subclass_of(self, class_name: str):
        return self.name == class_name or self.parent().is_subclass_of(class_name) or any(interface().is_subclass_of(class_name) for interface in self.interfaces)

    def prepare_use(self):
        if self.class_init_complete: return
        self.class_init_complete = True

        if ("<clinit>", "()V") in self.methods:
            try:
                import mcpython.loader.java.Runtime
            except ImportError:
                return

            runtime = mcpython.loader.java.Runtime.Runtime()
            runtime.run_method(self.get_method("<clinit>", "()V", inner=True))


class JavaClassInstance:
    def __init__(self, class_file: JavaBytecodeClass):
        self.class_file = class_file
        self.fields = {name: None for name in class_file.get_dynamic_field_keys()}

    def get_method(self, name: str, signature: str):
        return self.class_file.get_method(name, signature)

    def __repr__(self):
        return f"JavaByteCodeClassInstance(of={self.class_file})"

    def get_class(self):
        return self.class_file


def decode_cp_constant(const):
    if const[0] == 7:  # Class
        return vm.get_class(const[1][1])
    elif const[0] in (1, 3, 4, 5, 6, 8):
        return const[1][1] if isinstance(const[1], list) else const[1]
    raise NotImplementedError(const)


vm = JavaVM()
