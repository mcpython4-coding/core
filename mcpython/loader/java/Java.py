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
import copy

# Framework for loading and executing java bytecode
# Mainly independent from mcpython's source
# See Runtime.py for a system for executing the bytecode
# See builtin folder for python implementations for java internals
import ctypes
import struct
import sys
import traceback
import types
import typing
from abc import ABC

from mcpython.loader.java.JavaExceptionStack import StackCollectingException

# With this flag, the vm will do some fancy stuff when encountering unknown natives, trying to create
# a empty method and outputting an empty method body in the log for later implementation
DYNAMIC_NATIVES = "--fill-unknown-natives" in sys.argv

# some structs used all over the place
U1 = struct.Struct("!B")
U1_S = struct.Struct("!b")
U1_S_4 = struct.Struct("!bbbb")
U2 = struct.Struct("!H")
U2_S = struct.Struct("!h")
U4 = struct.Struct("!I")
U4_S = struct.Struct(">i")

# these are special values treated here
INT = struct.Struct("!i")
FLOAT = struct.Struct("!f")
LONG = struct.Struct("!q")
DOUBLE = struct.Struct("!d")


# Helper functions for above structs to pop from bytearray
def pop_u1(data: bytearray):
    e = data[:1]
    del data[0]
    return U1.unpack(e)[0]


def pop_u2_s(data: bytearray):
    e = data[:2]
    del data[:2]
    return U2_S.unpack(e)[0]


def pop_u2(data: bytearray):
    e = data[:2]
    del data[:2]
    return U2.unpack(e)[0]


def pop_u4(data: bytearray) -> int:
    e = data[:4]
    del data[:4]
    return U4.unpack(e)[0]


def pop_u4_s(data: bytearray):
    e = data[:4]
    del data[:4]
    return U4_S.unpack(e)[0]


def pop_sized(size: int, data: bytearray):
    e = data[:size]
    del data[:size]
    return bytes(e)


def pop_struct(s: struct.Struct, data: bytearray):
    return s.unpack(pop_sized(s.size, data))


# You can override this methods from outside this file to do your own logging, but this is the way to go now...
# (Mcpython wraps them around its internal logger)
def warn(text: str):
    print("[JAVA][WARN]", warn)


def info(text: str):
    pass


# And this can be wrapped into your own resource access (multiple directories, web download, whatever you want)
# (Mcpython wraps it around the general resource access implementation called ResourceLoader)
def get_bytecode_of_class(class_name: str):
    with open("./" + class_name.replace(".", "/") + ".class", mode="rb") as f:
        return f.read()


class JavaVM:
    """
    The java VM, as specified by https://docs.oracle.com/javase/specs/index.html

    Currently, only java bytecode below (and including) java 16 can be loaded

    The JVM is capable of providing non-bytecode classes via the Native system (or for really fancy work,
    own AbstractJavaClass implementations)

    The default implementation for java bytecode is located in this file
    It loads the bytecode as outlined by above document of oracle
    """

    def __init__(self):
        self.debugged_methods = set()
        self.shared_classes: typing.Dict[
            str, typing.Union["AbstractJavaClass", typing.Type]
        ] = {}
        self.classes_by_version: typing.Dict[
            typing.Hashable, typing.Dict[str, "AbstractJavaClass"]
        ] = {}
        self.lazy_classes: typing.Set[typing.Tuple[typing.Any, str]] = set()

        self.array_helper = JavaArrayManager(self)

    def load_lazy(self):
        while len(self.lazy_classes) > 0:
            version, name = self.lazy_classes.pop()
            self.get_class(name, version=version)

    def init_builtins(self):
        from mcpython.loader.java.builtin.java.io import (
            BufferedWriter,
            File,
            FileInputStream,
            FileOutputStream,
            OutputStreamWriter,
            Path,
            PushbackInputStream,
            Reader,
        )
        from mcpython.loader.java.builtin.java.lang import (
            Boolean,
            Character,
            Class,
            Deprecated,
            Double,
            Enum,
            FunctionalInterface,
            IllegalStateException,
            Integer,
            Math,
            Object,
            RuntimeException,
            String,
            System,
            ThreadLocal,
        )
        from mcpython.loader.java.builtin.java.lang.annotation import (
            Documented,
            ElementType,
            Retention,
            RetentionPolicy,
            Target,
            Repeatable,
            Inherited,
        )
        from mcpython.loader.java.builtin.java.lang.reflect import Method, Field
        from mcpython.loader.java.builtin.java.nio.file import Files, Path, Paths
        from mcpython.loader.java.builtin.java.util import (
            ArrayList,
            Arrays,
            Collection,
            Collections,
            EnumMap,
            EnumSet,
            HashMap,
            HashSet,
            IdentityHashMap,
            Iterator,
            LinkedHashMap,
            LinkedList,
            List,
            Locale,
            Map,
            Objects,
            Optional,
            Random,
            Set,
            TreeMap,
            TreeSet,
            WeakHashMap,
            UUID,
            LinkedHashSet,
            ArrayDeque,
        )
        from mcpython.loader.java.builtin.java.util.concurrent import (
            ConcurrentHashMap,
            TimeUnit,
            CopyOnWriteArrayList,
        )
        from mcpython.loader.java.builtin.java.util.concurrent.atomic import (
            AtomicInteger,
        )
        from mcpython.loader.java.builtin.java.util.function import (
            BiFunction,
            Consumer,
            Function,
            Predicate,
            Supplier,
        )
        from mcpython.loader.java.builtin.java.util.regex import Pattern
        from mcpython.loader.java.builtin.java.util.stream import Collectors, Stream
        from mcpython.loader.java.builtin.java.text import DecimalFormat, DecimalFormatSymbols
        from mcpython.loader.java.builtin.java.awt import Color
        from mcpython.loader.java.builtin.java.math import RoundingMode

        from mcpython.loader.java.builtin.javax.annotation import Nonnull, CheckForNull
        from mcpython.loader.java.builtin.javax.annotation.meta import TypeQualifierDefault

    def init_bridge(self):
        from mcpython.loader.java.bridge import util
        from mcpython.loader.java.bridge.client import rendering
        from mcpython.loader.java.bridge.codec import builder
        from mcpython.loader.java.bridge.event import content, registries
        from mcpython.loader.java.bridge.fml import capability, config, loading, network
        from mcpython.loader.java.bridge.lib import (
            apache,
            fastutil,
            google_collect,
            gson,
            logging,
            mixin,
            netty,
            nightconfig,
        )
        from mcpython.loader.java.bridge.misc import (
            commands,
            containers,
            crafting,
            dispenser,
            enchantments,
            loot,
            nbt,
            potions,
            tags,
        )
        from mcpython.loader.java.bridge.world import biomes, collection, world

    def get_class(self, name: str, version=0) -> "AbstractJavaClass":
        name = name.replace(".", "/")
        if name in self.shared_classes:
            cls = self.shared_classes[name]
        elif name in self.classes_by_version.setdefault(version, {}):
            cls = self.classes_by_version[version][name]
        else:
            cls = self.load_class(name, version=version)

        cls.prepare_use()

        return cls

    def get_lazy_class(self, name: str, version: typing.Any = 0):
        self.lazy_classes.add((version, name))
        return lambda: self.get_class(name, version=version)

    def load_class(
        self, name: str, version: typing.Any = 0, shared=False
    ) -> "AbstractJavaClass":
        name = name.replace(".", "/")
        if name.startswith("["):
            return self.array_helper.get(name)

        try:
            bytecode = get_bytecode_of_class(name)
        except FileNotFoundError:
            if DYNAMIC_NATIVES:

                class Dynamic(NativeClass):
                    NAME = name

                print(
                    f"""
Native Dynamic Builder: Class {name} (not found)
Add into file and add to import list in natives:
from mcpython import shared
from mcpython.loader.java.Java import NativeClass, native

class {name.split('/')[-1].replace('$', '__')}(NativeClass):
    NAME = \"{name}\""""
                )

                return self.shared_classes[name]

            raise StackCollectingException(f"class {name} not found!") from None

        info("loading java class '" + name + "'")

        cls = JavaBytecodeClass()
        cls.internal_version = version
        cls.vm = self

        try:
            cls.from_bytes(bytearray(bytecode))
        except StackCollectingException as e:
            e.add_trace(f"decoding class {name}")
            raise

        if not shared:
            self.classes_by_version.setdefault(version, {})[name] = cls
        else:
            self.shared_classes[name] = cls

        try:
            cls.bake()
            cls.validate_class_file()
        except StackCollectingException as e:
            e.add_trace(f"baking class {name}")
            raise

        info(f"class load of class '{name}' finished")

        return cls

    def register_native(self, n: typing.Type["NativeClass"], version=None):
        instance = n()
        instance.internal_version = version
        if version is None:
            self.shared_classes[n.NAME] = instance
        else:
            self.classes_by_version.setdefault(version, {})[n.NAME] = instance

    def get_method_of_nat(self, nat, version: typing.Any = 0):
        cls = nat[1][1][1]
        name = nat[2][1][1]
        descriptor = nat[2][2][1]
        cls = self.get_class(cls, version=version)
        return cls.get_method(name, descriptor)

    def debug_method(self, cls: str, name: str, sig: str):
        self.debugged_methods.add((cls, name, sig))


class AbstractJavaClass:
    """
    Abstract base class for java classes handled by the vm
    """

    def __init__(self):
        self.name: str = None   # the class name
        self.file_source: str = None  # a path to the file this class was loaded from
        self.parent = None  # the parent of the class
        self.interfaces: typing.List[typing.Callable[[], typing.Optional[AbstractJavaClass]]] = []
        self.internal_version = 0  # the internal version identifier
        self.vm = None  # the vm instance bound to

    def get_method(self, name: str, signature: str, inner=False):
        raise NotImplementedError

    def get_static_attribute(self, name: str, expected_type=None):
        raise NotImplementedError

    def set_static_attribute(self, name: str, value):
        raise NotImplementedError

    def create_instance(self):
        raise NotImplementedError

    def on_annotate(self, cls, args):
        if DYNAMIC_NATIVES:
            print("\n" + self.name + " is missing on_annotate implementation!")
            return

        raise RuntimeError((self, cls, args))

    def get_dynamic_field_keys(self):
        return set()

    def is_subclass_of(self, class_name: str) -> bool:
        raise NotImplementedError

    def prepare_use(self, runtime=None):
        pass


class NativeClass(AbstractJavaClass, ABC):
    NAME = None
    EXPOSED_VERSIONS: typing.Optional[set] = None

    @classmethod
    def __init_subclass__(cls, **kwargs):
        if cls.NAME is not None:

            if cls.EXPOSED_VERSIONS is None:
                vm.register_native(cls)
            else:
                # todo: add flag to share native
                for version in cls.EXPOSED_VERSIONS:
                    vm.register_native(cls, version)

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
            try:
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

                else:
                    return m

            except StackCollectingException as e:
                e.add_trace(f"not found up at {self.name}")
                raise

        if DYNAMIC_NATIVES:

            def dynamic(*_):
                pass

            self.exposed_methods[(name, signature)] = dynamic

            dynamic.native_name = name
            dynamic.native_signature = signature

            print(
                f"""
Native Dynamic Builder: Class {self.name}
Method {name} with signature {signature}
Add:
    @native(\"{name}\", \"{signature}\")
    def {name.removeprefix("<").removesuffix(">").replace("$", "__")}(self, *_):
        pass"""
            )

            return dynamic

        raise StackCollectingException(
            f"class {self.name} has no method named '{name}' with signature {signature}"
        ).add_trace(str(self)).add_trace(
            str(list(self.exposed_methods.keys()))
        ) from None

    def get_static_attribute(self, name: str, expected_type=None):
        if name not in self.exposed_attributes:
            if DYNAMIC_NATIVES:
                print(
                    f"""
Native Dynamic Builder: Class {self.name}
Static attribute {name}"""
                )
                self.exposed_attributes[name] = None
                return

            raise StackCollectingException(
                f"unknown static attribute '{name}' of class '{self.name}' (expected type: {expected_type})"
            )

        return self.exposed_attributes[name]

    def set_static_attribute(self, name: str, value):
        self.exposed_attributes[name] = value

    def create_instance(self):
        return NativeClassInstance(self)

    def __repr__(self):
        return f"NativeClass({self.NAME})"

    def is_subclass_of(self, class_name: str):
        return self.name == class_name

    def iter_over_instance(self, instance) -> typing.Iterable:
        raise StackCollectingException(f"unable to iterate over {instance}")


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


def native(name: str, signature: str, static=False):
    def setup(method):
        method.native_name = name
        method.native_signature = signature
        method.access = 0x1101 | (0 if not static else 0x0008)  # public native synthetic (static)
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

    def __init__(self, vm_i: JavaVM):
        self.vm = vm_i

    def get(self, class_text: str, version=0):
        depth = class_text.count("[")
        cls_name = class_text[depth:]
        cls = self.vm.get_class(
            cls_name.removeprefix("L").removesuffix(";"), version=version
        )

        instance = ArrayBase(depth, class_text, cls)

        self.vm.shared_classes[class_text] = instance
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
        self.table: "JavaAttributeTable" = None
        self.max_stacks = 0
        self.max_locals = 0
        self.code: bytes = None
        self.exception_table = {}
        self.attributes = JavaAttributeTable(self)

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        self.table = table
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
        # as by https://docs.oracle.com/javase/specs/jvms/se16/html/jvms-4.html#jvms-4.7.16

        self.tag = tag = chr(pop_u1(data))

        # these can be directly loaded from the constant pool
        if tag in "BCDFIJSZs":
            self.data = decode_cp_constant(table.class_file.cp[pop_u2(data) - 1])

        elif tag == "e":
            cls_name = (
                table.class_file.cp[pop_u2(data) - 1][1]
                .removeprefix("L")
                .removesuffix(";")
            )
            attr_name = table.class_file.cp[pop_u2(data) - 1][1]

            cls = vm.get_class(cls_name, version=table.class_file.internal_version)
            self.data = cls.get_static_attribute(attr_name, "ENUM-ENTRY")
        elif tag == "c":
            self.data = table.class_file.cp[pop_u2(data) - 1]
        elif tag == "[":
            self.data = [ElementValue().parse(table, data) for _ in range(pop_u2(data))]
        elif tag == "@":
            annotation_type = (
                table.class_file.cp[pop_u2(data) - 1][1]
                .removeprefix("L")
                .removesuffix(";")
            )

            values = []

            for _ in range(pop_u2(data)):
                name = table.class_file.cp[pop_u2(data) - 1]
                if name[0] != 1:
                    raise StackCollectingException("invalid ")
                name = name[1]
                value = ElementValue().parse(table, data)
                values.append((name, value))

            self.data = annotation_type, values
        else:
            raise NotImplementedError(tag)

        return self


class RuntimeVisibleAnnotationsParser(AbstractAttributeParser):
    def __init__(self):
        self.annotations = []

    def parse(self, table: "JavaAttributeTable", data: bytearray):
        for _ in range(pop_u2(data)):
            annotation_type = (
                table.class_file.cp[pop_u2(data) - 1][1]
                .removeprefix("L")
                .removesuffix(";")
            )

            values = []

            for _ in range(pop_u2(data)):
                name = table.class_file.cp[pop_u2(data) - 1]
                if name[0] != 1:
                    raise StackCollectingException(
                        f"invalid name @annotation head for ElementValue pair: {name}"
                    )

                name = name[1]

                try:
                    value = ElementValue().parse(table, data)
                except StackCollectingException as e:
                    e.add_trace(
                        f"during decoding {self.__class__.__name__}-attribute for annotation class {annotation_type} annotating class {table.class_file.name}"
                    )
                    raise

                values.append((name, value))

            self.annotations.append((annotation_type, values))

        return self


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

    def invoke(self, *args):
        import mcpython.loader.java.Runtime

        runtime = mcpython.loader.java.Runtime.Runtime()
        return runtime.run_method(self, *args)

    def get_class(self):
        return self.class_file.vm.get_class(
            "java/lang/reflect/Method", version=self.class_file.internal_version
        )

    def __call__(self, *args):
        return self.invoke(*args)


class JavaBytecodeClass(AbstractJavaClass):
    def __init__(self):
        super().__init__()
        self.cp: typing.List[typing.Any] = []
        self.access = 0
        self.methods = {}
        self.fields = {}

        # can hold a list of fields
        self.enum_fields: typing.Optional[typing.List[JavaField]] = None

        self.dynamic_field_keys = set()
        self.static_field_values = {}
        self.attributes = JavaAttributeTable(self)

        self.on_bake = []
        self.on_instance_creation = []

        self.class_init_complete = False

        self.is_public = True
        self.is_final = False
        self.is_special_super = False
        self.is_interface = False
        self.is_abstract = False
        self.is_synthetic = False
        self.is_annotation = False
        self.is_enum = False
        self.is_module = False

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
                d = tag, e.decode("utf-8", errors="ignore")
            elif tag == 15:
                d = tag, pop_u1(data), pop_u2(data)
            else:
                raise ValueError(tag)

            self.cp[j] = list(d)

        for i, e in enumerate(self.cp):
            if e is None:
                continue

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

        # As by https://docs.oracle.com/javase/specs/jvms/se16/html/jvms-4.html#jvms-4.1-200-E.1
        self.access |= pop_u2(data)
        self.is_public = bool(self.access & 0x0001)
        self.is_final = bool(self.access & 0x0010)
        self.is_special_super = bool(self.access & 0x0020)
        self.is_interface = bool(self.access & 0x0200)
        self.is_abstract = bool(self.access & 0x0400)
        self.is_synthetic = bool(self.access & 0x1000)
        self.is_annotation = bool(self.access & 0x2000)
        self.is_enum = bool(self.access & 0x4000)
        self.is_module = bool(self.access & 0x8000)

        self.name: str = self.cp[pop_u2(data) - 1][1][1]
        self.parent: typing.Callable[[], typing.Optional[AbstractJavaClass]] = vm.get_lazy_class(
            self.cp[pop_u2(data) - 1][1][1], version=self.internal_version
        )

        self.interfaces += [
            vm.get_lazy_class(
                self.cp[pop_u2(data) - 1][1][1], version=self.internal_version
            )
            for _ in range(pop_u2(data))
        ]

        if self.is_enum:
            self.enum_fields = []

        for _ in range(pop_u2(data)):
            field = JavaField()
            field.from_data(self, data)

            if field.access & 0x4000:
                self.enum_fields.append(field)

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

        try:
            m = self.parent().get_method(*des) if self.parent is not None else None
        except StackCollectingException as e:
            for interface in self.interfaces:
                try:
                    m = interface().get_method(*des)
                except StackCollectingException:
                    pass
                else:
                    break
            else:
                e.add_trace(f"not found up in {self.name}")
                raise

        if m is not None:
            return m

        raise StackCollectingException(f"class {self.name} has not method {name} with signature {signature}")

    def get_static_attribute(self, name: str, expected_type=None):
        if name not in self.static_field_values:
            if self.parent is not None:
                try:
                    return self.parent().get_static_attribute(name)
                except KeyError:
                    pass

            # interfaces do not provide fields, don't they?

        try:
            return self.static_field_values[name]
        except KeyError:
            raise StackCollectingException(f"class {self.name} has no attribute {name} (class instance: {self})") from None

    def set_static_attribute(self, name: str, value):
        self.static_field_values[name] = value

    def bake(self):
        """
        Helper method for setting up a class
        Does some fancy work on annotations
        """

        for method in self.on_bake:
            method(self)

        self.on_bake.clear()

        if "RuntimeVisibleAnnotations" in self.attributes.attributes:
            for annotation in self.attributes["RuntimeVisibleAnnotations"]:
                for cls_name, args in annotation.annotations:
                    try:
                        cls = vm.get_class(cls_name, version=self.internal_version)
                    except StackCollectingException as e:
                        # checks if the class exists, this will be true if it is a here class loader exception
                        if (
                            e.text.startswith("class ")
                            and e.text.endswith(" not found!")
                            and len(e.traces) == 0
                        ):
                            # todo: can we do something else here, maybe add a flag to get_class to return None if the class
                            #   could not be loaded -> None check here
                            print("classloading exception for annotation ignored")
                            print(e.format_exception())
                        else:
                            e.add_trace(
                                f"runtime visible annotation handling @class {self.name} loading class {cls_name}"
                            )
                            raise
                    else:
                        cls.on_annotate(self, args)

    def create_instance(self):
        # Abstract classes cannot have instances
        if self.is_abstract:
            raise StackCollectingException(f"class {self.name} is abstract, so we cannot create an instance of it!")

        return JavaClassInstance(self)

    def __repr__(self):
        return f"JavaBytecodeClass({self.name},access={bin(self.access)},parent={self.parent()},interfaces=[{', '.join(repr(e()) for e in self.interfaces)}])"

    def get_dynamic_field_keys(self):
        return self.dynamic_field_keys | self.parent().get_dynamic_field_keys()

    def is_subclass_of(self, class_name: str):
        return (
            self.name == class_name
            or self.parent().is_subclass_of(class_name)
            or any(
                interface().is_subclass_of(class_name) for interface in self.interfaces
            )
        )

    def prepare_use(self, runtime=None):
        """
        Method for late-init-ing some stuff
        Can be called more than one time, only the first time will do stuff
        :param runtime: optional, the runtime instance to use during invoking the class init method when arrival

        todo: maybe load the function bytecode also here?
        """

        if self.class_init_complete:
            return

        self.class_init_complete = True

        if ("<clinit>", "()V") in self.methods:
            if runtime is None:
                try:
                    import mcpython.loader.java.Runtime
                except ImportError:
                    # If we have no way to invoke bytecode, don't do so
                    return

                runtime = mcpython.loader.java.Runtime.Runtime()

            try:
                runtime.run_method(self.get_method("<clinit>", "()V", inner=True))
            except StackCollectingException as e:
                e.add_trace(f"during class init of {self.name}")
                raise

    def validate_class_file(self):
        """
        Validation script on the overall class file

        Method validation happens during each method optimisation, starting at first method invocation,
            or some script interacting with it.
        """

        # validates the access flags
        if self.is_module:
            return

        if self.is_interface:
            if not self.is_abstract:
                raise RuntimeError(f"class {self.name} is interface, but not abstract")

            if self.is_final:
                raise RuntimeError(f"class {self.name} is interface and final, which is not allowed")

            if self.is_special_super:
                raise RuntimeError(f"class {self.name} is interface and special-super-handling, which is not allowed")

            if self.is_enum:
                raise RuntimeError(f"class {self.name} is interface and an enum, which is not allowed")

        else:
            if self.is_abstract and self.is_final:
                raise RuntimeError(f"class {self.name} is abstract and final, which is not allowed")


class JavaClassInstance:
    """
    An instance of a java bytecode class
    Wires down some stuff to the underlying class and holds the dynamic field values

    todo: add abstract base so natives can share the same layout
    todo: add set/get for fields & do type validation
    """

    def __init__(self, class_file: JavaBytecodeClass):
        self.class_file = class_file
        self.fields = {name: None for name in class_file.get_dynamic_field_keys()}

    def get_method(self, name: str, signature: str):
        return self.class_file.get_method(name, signature)

    def __repr__(self):
        return f"JavaByteCodeClassInstance(of={self.class_file})"

    def get_class(self):
        return self.class_file


def decode_cp_constant(const, version=0):
    """
    Helper code for decoding an arbitrary constant pool entry down to a "primitive"
    Used in the instructions directly loading from the runtime constant pool and storing the stuff
    in the runtime.
    :param const: the const, as stored in the constant pool
    :param version: the internal version of the class system, to use when loading a class
    :return: the primitive
    :raises NotImplementedError: when the constant pool entry could not be decoded with this decoded
    """

    if const[0] == 7:  # Class
        return vm.get_class(const[1][1], version=version)
    elif const[0] in (1, 3, 4, 5, 6, 8):
        return const[1][1] if isinstance(const[1], list) else const[1]
    raise NotImplementedError(const)


vm = JavaVM()
# this is the way how to attach a debugger to a certain method
# vm.debug_method("com/jaquadro/minecraft/storagedrawers/block/EnumCompDrawer", "<clinit>", "()V")
# vm.debug_method("appeng/core/api/definitions/ApiParts", "constructColoredDefinition", "(Ljava/lang/String;Ljava/lang/Class;Ljava/util/function/Function;)Lappeng/api/util/AEColoredItemDefinition;")
