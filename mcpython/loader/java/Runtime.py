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
import asyncio
import sys
import traceback
import typing
from abc import ABC

import mcpython.loader.java.Java
from mcpython.loader.java.JavaExceptionStack import StackCollectingException

DEBUG = "--debug-vm" in sys.argv


class UnhandledInstructionException(Exception):
    pass


class Runtime:
    """
    A Runtime is a "frame" in the current VM
    Each thread needs an own Runtime
    A Runtime hold the "flow" between methods
    """

    def __init__(self):
        self.stacks: typing.List["Stack"] = []

    def spawn_stack(self):
        stack = Stack()
        stack.runtime = self
        self.stacks.append(stack)
        return stack

    def run_method(
        self,
        method: typing.Union[mcpython.loader.java.Java.JavaMethod, typing.Callable],
        *args,
    ):
        if callable(method):
            from mcpython.common.mod.ModLoader import LoadingInterruptException
            try:
                return method(*args)
            except StackCollectingException as e:
                e.add_trace("invoking native " + str(method) + " with " + str(args))
                raise
            except (LoadingInterruptException, SystemExit):
                raise
            except:
                raise StackCollectingException(
                    f"during invoking native {method} with {args}"
                )

        if method.code_repr is None:
            method.code_repr = BytecodeRepr(method.attributes["Code"][0])

        stack = self.spawn_stack()

        stack.code = method.code_repr
        stack.method = method
        method.code_repr.prepare_stack(stack)
        stack.local_vars[: len(args)] = list(args)

        stack.run()

        return stack.return_value

    def get_arg_parts_of(
        self,
        method: typing.Union[mcpython.loader.java.Java.JavaMethod, typing.Callable],
    ) -> typing.Iterator[str]:
        if hasattr(method, "signature"):
            signature = method.signature
        elif hasattr(method, "native_signature"):
            signature = method.native_signature
        else:
            raise ValueError(method)

        v = signature.removeprefix("(").split(")")[0]
        i = 0
        start = 0
        while i < len(v):
            is_array = False

            if v[i] == "[":
                is_array = True

            if v[i] == "L":
                i = v.index(";", i) + 1
                yield v[start:i], False
            else:
                i += 1
                if not is_array:
                    yield v[start:i], v[i - 1] in "DJ"

            if not is_array:
                start = i

    def parse_args_from_stack(self, method, stack, static=False):
        parts = tuple(self.get_arg_parts_of(method))
        previous_count = len(stack.stack)

        try:
            args = [stack.pop() for _ in range(len(parts))]

            if not static:
                args.append(stack.pop())

        except IndexError:
            print(method, stack.stack, static, previous_count, len(parts), parts)
            raise

        if isinstance(method, mcpython.loader.java.Java.JavaMethod):
            offset = 0
            for i, (_, state) in enumerate(parts):
                if state:
                    args.insert(i + offset, None)
                    offset += 1

        return tuple(reversed(args))


class Stack:
    def __init__(self):
        self.local_vars = []
        self.stack = []
        self.cp = 0

        self.code = None
        self.method = None

        import mcpython.loader.java.Java

        self.vm = mcpython.loader.java.Java.vm

        self.runtime: Runtime = None

        self.return_value = None

        self.code: "BytecodeRepr" = None

    def pop(self):
        if len(self.stack) == 0:
            raise StackCollectingException("StackUnderflowException")

        return self.stack.pop(-1)

    def push(self, value):
        self.stack.append(value)

    def end(self, value=None):
        self.cp = -1
        self.return_value = value

    def run(self):
        """
        Runs the data on this stack

        todo: add async variant
        """

        # todo: check for general debugging & class debugging
        debugging = (
            DEBUG
            or (self.method.class_file.name, self.method.name, self.method.signature)
            in self.method.class_file.vm.debugged_methods
        )

        # todo: is this really needed?
        self.method.class_file.prepare_use()
        if debugging:
            mcpython.loader.java.Java.warn(("launching method", self.method))

        while self.cp != -1:
            instruction = self.code.decoded_code[self.cp]

            if debugging:
                mcpython.loader.java.Java.warn(
                    "instruction [info before invoke] " + str((self.cp, instruction))
                )
                mcpython.loader.java.Java.warn("stack: " + str(self.stack)[:200])
                mcpython.loader.java.Java.warn("local: " + str(self.local_vars)[:200])

            try:
                result = instruction[0].invoke(instruction[1], self)
            except StackCollectingException as e:
                e.add_trace(
                    f"during invoking {instruction[0]} in {self.method} [index: {self.cp}]"
                )
                e.add_trace(str(instruction[1]))
                raise

            if not result and self.cp != -1:
                self.cp += instruction[2]

        if debugging:
            mcpython.loader.java.Java.warn(
                ("finished method", self.method, self.return_value)
            )


class Instruction(ABC):
    OPCODES: typing.Set[int] = set()

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return None, 1

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        raise NotImplementedError


class CPLinkedInstruction(Instruction, ABC):
    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return (
            class_file.cp[
                mcpython.loader.java.Java.U2.unpack(data[index + 1 : index + 3])[0] - 1
            ],
            3,
        )


class BytecodeRepr:
    OPCODES: typing.Dict[int, typing.Type[Instruction]] = {}

    @classmethod
    def register_instruction(cls, instr: typing.Type[Instruction]):
        for opcode in instr.OPCODES:
            cls.OPCODES[opcode] = instr
        return instr

    def __init__(self, code: mcpython.loader.java.Java.CodeParser):
        self.code = code

        self.decoded_code: typing.List[
            typing.Optional[typing.Tuple[Instruction, typing.Any, int]]
        ] = [None] * len(code.code)

        code = bytearray(code.code)
        i = 0
        while i < len(code):
            tag = code[i]

            if tag in self.OPCODES:
                instr = self.OPCODES[tag]
                data, size = instr.decode(code, i, self.code.class_file)

                self.decoded_code[i] = (instr, data, size)

                i += size

            else:
                raise StackCollectingException(
                    "invalid instruction: "
                    + str(hex(tag))
                    + " (following bits: "
                    + str(code[i : i + 5])
                    + ")"
                )

    def prepare_stack(self, stack: Stack):
        stack.local_vars = [None] * self.code.max_locals
        stack.cp = 0
        stack.code = self


# Now, the instruction implementations


class ConstPush(Instruction, ABC):
    PUSHES = None

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(cls.PUSHES)


@BytecodeRepr.register_instruction
class AConstNull(ConstPush):
    OPCODES = {0x01}


@BytecodeRepr.register_instruction
class IConstM1(ConstPush):
    OPCODES = {0x02}
    PUSHES = -1


@BytecodeRepr.register_instruction
class IConst0(ConstPush):
    OPCODES = {0x03, 0x0E}
    PUSHES = 0


@BytecodeRepr.register_instruction
class IConst1(ConstPush):
    OPCODES = {0x04, 0x0F}
    PUSHES = 1


@BytecodeRepr.register_instruction
class IConst2(ConstPush):
    OPCODES = {0x05}
    PUSHES = 2


@BytecodeRepr.register_instruction
class IConst3(ConstPush):
    OPCODES = {0x06}
    PUSHES = 3


@BytecodeRepr.register_instruction
class IConst4(ConstPush):
    OPCODES = {0x07}
    PUSHES = 4


@BytecodeRepr.register_instruction
class IConst5(ConstPush):
    OPCODES = {0x08}
    PUSHES = 5


@BytecodeRepr.register_instruction
class FConst0(ConstPush):
    OPCODES = {0x0B}
    PUSHES = 0.0


@BytecodeRepr.register_instruction
class FConst1(ConstPush):
    OPCODES = {0x0C}
    PUSHES = 1.0


@BytecodeRepr.register_instruction
class FConst2(ConstPush):
    OPCODES = {0x0D}
    PUSHES = 2.0


@BytecodeRepr.register_instruction
class BiPush(Instruction):
    OPCODES = {0x10}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U1_S.unpack(data[index + 1 : index + 2])[0], 2

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(data)


@BytecodeRepr.register_instruction
class SiPush(Instruction):
    OPCODES = {0x11}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(data)


@BytecodeRepr.register_instruction
class LDC(Instruction):
    OPCODES = {0x12}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return data[index + 1], 2

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(
            mcpython.loader.java.Java.decode_cp_constant(
                stack.method.class_file.cp[data - 1],
                version=stack.method.class_file.internal_version,
            )
        )


@BytecodeRepr.register_instruction
class LDC_W(Instruction):
    OPCODES = {0x13, 0x14}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(
            mcpython.loader.java.Java.decode_cp_constant(
                stack.method.class_file.cp[data - 1],
                version=stack.method.class_file.internal_version,
            )
        )


@BytecodeRepr.register_instruction
class ArrayLoad(Instruction):
    OPCODES = {0x32}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        index = stack.pop()
        array = stack.pop()
        stack.push(array[index])


@BytecodeRepr.register_instruction
class ArrayStore(Instruction):
    OPCODES = {0x53, 0x4F}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        value = stack.pop()
        index = stack.pop()
        array = stack.pop()
        array[index] = value


@BytecodeRepr.register_instruction
class Load(Instruction):
    OPCODES = {0x19, 0x15, 0x18}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U1.unpack(data[index + 1 : index + 2])[0], 2

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(stack.local_vars[data])


@BytecodeRepr.register_instruction
class Load0(Instruction):
    OPCODES = {0x2A, 0x1A, 0x22, 0x26}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(stack.local_vars[0])


@BytecodeRepr.register_instruction
class Load1(Instruction):
    OPCODES = {0x2B, 0x1B, 0x23, 0x27}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(stack.local_vars[1])


@BytecodeRepr.register_instruction
class Load2(Instruction):
    OPCODES = {0x2C, 0x1C, 0x24, 0x28}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(stack.local_vars[2])


@BytecodeRepr.register_instruction
class Load3(Instruction):
    OPCODES = {0x2D, 0x1D, 0x25, 0x29}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(stack.local_vars[3])


@BytecodeRepr.register_instruction
class Store(Instruction):
    OPCODES = {0x3A, 0x36}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U1.unpack(data[index + 1 : index + 2])[0], 2

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.local_vars[data] = stack.pop()


@BytecodeRepr.register_instruction
class Store0(Instruction):
    OPCODES = {0x4B, 0x3B}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.local_vars[0] = stack.pop()


@BytecodeRepr.register_instruction
class Store1(Instruction):
    OPCODES = {0x4C, 0x3C}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.local_vars[1] = stack.pop()


@BytecodeRepr.register_instruction
class Store2(Instruction):
    OPCODES = {0x4D, 0x3D}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.local_vars[2] = stack.pop()


@BytecodeRepr.register_instruction
class Store3(Instruction):
    OPCODES = {0x4E, 0x3E}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.local_vars[3] = stack.pop()


@BytecodeRepr.register_instruction
class POP(Instruction):
    OPCODES = {0x57}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.pop()


@BytecodeRepr.register_instruction
class DUP(Instruction):
    OPCODES = {0x59}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        v = stack.pop()
        stack.push(v)
        stack.push(v)


@BytecodeRepr.register_instruction
class IADD(Instruction):
    OPCODES = {0x60}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        b, a = stack.pop(), stack.pop()
        stack.push(a + b)


@BytecodeRepr.register_instruction
class IDIV(Instruction):
    OPCODES = {0x6C}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        b, a = stack.pop(), stack.pop()
        stack.push(a // b)


@BytecodeRepr.register_instruction
class IINC(Instruction):
    OPCODES = {0x84}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return (
            data[index + 1],
            mcpython.loader.java.Java.U1_S.unpack(data[index + 2 : index + 3])[0],
        ), 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.local_vars[data[0]] += data[1]


@BytecodeRepr.register_instruction
class IfGe(Instruction):
    OPCODES = {0xA2}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        if stack.pop() <= stack.pop():
            stack.cp += data
            return True


@BytecodeRepr.register_instruction
class IfLe(Instruction):
    OPCODES = {0xA4}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        if stack.pop() >= stack.pop():
            stack.cp += data
            return True


@BytecodeRepr.register_instruction
class IfEq(Instruction):
    OPCODES = {0xA5}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        if stack.pop() == stack.pop():
            stack.cp += data
            return True


@BytecodeRepr.register_instruction
class IfNEq(Instruction):
    OPCODES = {0xA6}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        if stack.pop() != stack.pop():
            stack.cp += data
            return True


@BytecodeRepr.register_instruction
class IfEq0(Instruction):
    OPCODES = {0x99}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        if stack.pop() == 0:
            stack.cp += data
            return True


@BytecodeRepr.register_instruction
class IfNEq0(Instruction):
    OPCODES = {0x9A}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        if stack.pop() != 0:
            stack.cp += data
            return True


@BytecodeRepr.register_instruction
class Goto(Instruction):
    OPCODES = {0xA7}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.cp += data
        return True


@BytecodeRepr.register_instruction
class AReturn(Instruction):
    OPCODES = {0xB0, 0xAC}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.end(stack.pop())


@BytecodeRepr.register_instruction
class Return(Instruction):
    OPCODES = {0xB1}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.end()


@BytecodeRepr.register_instruction
class GetStatic(CPLinkedInstruction):
    OPCODES = {0xB2}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        cls_name = data[1][1][1]
        java_class = stack.vm.get_class(
            cls_name, version=stack.method.class_file.internal_version
        )
        name = data[2][1][1]
        stack.push(java_class.get_static_attribute(name, expected_type=data[2][2][1]))


@BytecodeRepr.register_instruction
class PutStatic(CPLinkedInstruction):
    OPCODES = {0xB3}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        cls_name = data[1][1][1]
        java_class = stack.vm.get_class(
            cls_name, version=stack.method.class_file.internal_version
        )
        name = data[2][1][1]
        value = stack.pop()
        java_class.set_static_attribute(name, value)


@BytecodeRepr.register_instruction
class GetField(CPLinkedInstruction):
    OPCODES = {0xB4}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        name = data[2][1][1]
        obj = stack.pop()
        try:
            stack.push(obj.fields[name])
        except KeyError:
            print(obj)
            raise


@BytecodeRepr.register_instruction
class PutField(CPLinkedInstruction):
    OPCODES = {0xB5}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        name = data[2][1][1]
        value = stack.pop()
        obj = stack.pop()
        obj.fields[name] = value


@BytecodeRepr.register_instruction
class InvokeVirtual(CPLinkedInstruction):
    OPCODES = {0xB6}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        method = stack.vm.get_method_of_nat(
            data, version=stack.method.class_file.internal_version
        )
        # todo: add args
        stack.push(
            stack.runtime.run_method(
                method, *stack.runtime.parse_args_from_stack(method, stack)
            )
        )


@BytecodeRepr.register_instruction
class InvokeSpecial(CPLinkedInstruction):
    OPCODES = {0xB7}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        method = stack.vm.get_method_of_nat(
            data, version=stack.method.class_file.internal_version
        )
        result = stack.runtime.run_method(
            method, *stack.runtime.parse_args_from_stack(method, stack)
        )
        if (method.name if hasattr(method, "name") else method.native_name) not in (
            "<init>",
            "<clinit>",
        ):
            stack.push(result)


@BytecodeRepr.register_instruction
class InvokeStatic(CPLinkedInstruction):
    OPCODES = {0xB8}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        method = stack.vm.get_method_of_nat(
            data, version=stack.method.class_file.internal_version
        )
        stack.push(
            stack.runtime.run_method(
                method, *stack.runtime.parse_args_from_stack(method, stack, static=True)
            )
        )


@BytecodeRepr.register_instruction
class InvokeInterface(CPLinkedInstruction):
    OPCODES = {0xB9}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return (
            class_file.cp[
                mcpython.loader.java.Java.U2.unpack(data[index + 1 : index + 3])[0] - 1
            ],
            data[index + 3],
        ), 5

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        method = stack.vm.get_method_of_nat(
            data[0], version=stack.method.class_file.internal_version
        )
        args = stack.runtime.parse_args_from_stack(method, stack)
        obj = args[0]

        try:
            method = obj.get_class().get_method(
                method.name if hasattr(method, "name") else method.native_name,
                method.signature
                if hasattr(method, "signature")
                else method.native_signature,
            )
        except StackCollectingException as e:
            print(e.format_exception())
        except AttributeError:
            pass

        stack.push(stack.runtime.run_method(method, *args))


@BytecodeRepr.register_instruction
class InvokeDynamic(CPLinkedInstruction):
    OPCODES = {0xBA}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return (
            class_file.cp[
                mcpython.loader.java.Java.U2.unpack(data[index + 1 : index + 3])[0] - 1
            ],
            5,
        )

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        boostrap = stack.method.class_file.attributes["BootstrapMethods"][0].entries[
            data[1]
        ]
        nat = data[2]
        # print(boostrap, "\n", nat)

        target_nat = boostrap[1][1][2][2]

        try:
            cls_file = stack.vm.get_class(
                boostrap[1][1][2][1][1][1],
                version=stack.method.class_file.internal_version,
            )
            method = cls_file.get_method(target_nat[1][1], target_nat[2][1])
        except StackCollectingException as e:
            e.add_trace(str(boostrap[0]))
            e.add_trace(str(boostrap[1]))
            e.add_trace(str(nat))
            raise
        except:
            e = StackCollectingException("during resolving invokedynamic")
            e.add_trace(str(boostrap[0]))
            e.add_trace(str(boostrap[1]))
            e.add_trace(str(nat))
            raise e

        stack.push(method)


@BytecodeRepr.register_instruction
class New(CPLinkedInstruction):
    OPCODES = {0xBB}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        c = stack.vm.get_class(
            data[1][1], version=stack.method.class_file.internal_version
        )
        stack.push(c.create_instance())


@BytecodeRepr.register_instruction
class NewArray(CPLinkedInstruction):
    OPCODES = {0xBC}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U1.unpack(data[index + 1 : index + 2])[0], 2

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push([None] * stack.pop())


@BytecodeRepr.register_instruction
class ANewArray(CPLinkedInstruction):
    OPCODES = {0xBD}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push([None] * stack.pop())


@BytecodeRepr.register_instruction
class ArrayLength(Instruction):
    OPCODES = {0xBE}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(len(stack.pop()))


@BytecodeRepr.register_instruction
class AThrow(Instruction):
    OPCODES = {0xBF}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        exception = stack.pop()
        stack.stack.clear()
        stack.push(exception)
        raise StackCollectingException("User raised exception", base=exception)


@BytecodeRepr.register_instruction
class CheckCast(CPLinkedInstruction):
    OPCODES = {0xC0}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        pass  # todo: implement


@BytecodeRepr.register_instruction
class InstanceOf(CPLinkedInstruction):
    OPCODES = {0xC1}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        obj = stack.pop()

        if not hasattr(obj, "get_class"):
            # todo: we need a fix here!
            stack.push(0)
        else:
            stack.push(int(obj is None or obj.get_class().is_subclass_of(data[1][1])))


@BytecodeRepr.register_instruction
class IfNull(Instruction):
    OPCODES = {0xC6}

    @classmethod
    def decode(
        cls, data: bytearray, index, class_file
    ) -> typing.Tuple[typing.Any, int]:
        return mcpython.loader.java.Java.U2_S.unpack(data[index + 1 : index + 3])[0], 3

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack) -> bool:
        if stack.pop() is None:
            stack.cp += data
            return True


@BytecodeRepr.register_instruction
class Mul(Instruction):
    OPCODES = {0x68}

    @classmethod
    def invoke(cls, data: typing.Any, stack: Stack):
        stack.push(stack.pop() * stack.pop())
