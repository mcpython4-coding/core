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
import dis
import types
import typing
import weakref
from collections import defaultdict

import pyglet
from mcpython.mixin.MixinMethodWrapper import MixinPatchHelper
from mcpython.mixin.PyBytecodeManipulator import FunctionPatcher
# RETURN_VALUE, RAISE_VARARGS
from mcpython.mixin.util import PyOpcodes

FLOW_INTERRUPT = [83, 130]

# SETUP_WITH, FOR_ITER, SETUP_FINALLY
FLOW_JUMP_CONDITIONAL_OFFSET = [143, 93, 122]

# POP_JUMP_IF_TRUE, POP_JUMP_IF_FALSE, JUMP_IF_NOT_EXC_MATCH, JUMP_IF_TRUE_OR_POP
# JUMP_IF_FALSE_OR_POP
FLOW_JUMP_CONDITIONAL_DIRECT = [143, 115, 114, 121, 112, 111]


class Branch:
    def __init__(self, container: "ControlFlowAnalyser"):
        self.container = container
        self.following_branches = weakref.WeakSet()
        self.instructions: typing.List[dis.Instruction] = []
        self.dataflow_for_instructions = []

        self.batch = None
        self.rendering_objects = []

    def add_instruction(self, instr: dis.Instruction):
        self.instructions.append(instr)
        self.dataflow_for_instructions.append(None)
        return self

    def prepare_rendering(self):
        self.batch = pyglet.graphics.Batch()

    def draw(self):
        self.batch.draw()

    def prepare_dataflow(self, tracker: "StackAnalyserTracker"):
        for instr in self.instructions:
            match instr.opcode:
                case PyOpcodes.POP_TOP:
                    tracker.pop()

                case PyOpcodes.ROT_TWO:
                    a = tracker.pop()
                    b = tracker.pop()
                    tracker.push(a)
                    tracker.push(b)

                case PyOpcodes.ROT_THREE:
                    a = tracker.pop()
                    b = tracker.pop()
                    c = tracker.pop()
                    tracker.push(a)
                    tracker.push(c)
                    tracker.push(b)

                case PyOpcodes.ROT_FOUR:
                    a = tracker.pop()
                    b = tracker.pop()
                    c = tracker.pop()
                    d = tracker.pop()
                    tracker.push(a)
                    tracker.push(d)
                    tracker.push(c)
                    tracker.push(b)

                case PyOpcodes.DUP_TOP:
                    a = tracker.pop()
                    tracker.push(a)
                    tracker.push(a)

                case PyOpcodes.DUP_TOP_TWO:
                    a = tracker.pop()
                    b = tracker.pop()
                    tracker.push(b)
                    tracker.push(a)
                    tracker.push(b)
                    tracker.push(a)


class IDataFlowDataSource:
    pass


class StackAnalyserTracker:
    def __init__(self):
        self.stack_data_flow: typing.List[IDataFlowDataSource] = []

    def pop(self):
        return self.stack_data_flow.pop(-1)

    def push(self, value: IDataFlowDataSource):
        self.stack_data_flow.append(value)
        return self


class ConstantDataSource(IDataFlowDataSource):
    def __init__(self):
        self.value = ...


class InvokeResultSource(IDataFlowDataSource):
    def __init__(self):
        self.body_ref: str = None

        # For non-static methods, this holds the IDataFlowDataSource to the object used as "self"
        self.this_source: IDataFlowDataSource | None = None

        self.arg_sources: typing.List[IDataFlowDataSource] = []
        self.kwarg_sources: typing.Dict[str, IDataFlowDataSource] = {}

        # The args with a * or a ** in front
        self.star_args: typing.Tuple[IDataFlowDataSource | None, IDataFlowDataSource |None ] = None, None


class IterItemSource(IDataFlowDataSource):
    def __init__(self):
        self.iter_source: IDataFlowDataSource = None


class IterUnpackSource(IDataFlowDataSource):
    def __init__(self):
        self.iter_source: IDataFlowDataSource = None
        self.iter_item = 0


class AttributSource(IDataFlowDataSource):
    def __init__(self):
        self.name: str = None
        self.target: IDataFlowDataSource = None


class ModuleImportSource(IDataFlowDataSource):
    def __init__(self):
        self.module_name: str = None


class ControlFlowAnalyser:
    def __init__(
        self,
        target: typing.Union[types.FunctionType, FunctionPatcher, MixinPatchHelper],
    ):
        if isinstance(target, types.FunctionType):
            self.helper = MixinPatchHelper(FunctionPatcher(target))
        elif isinstance(target, FunctionPatcher):
            self.helper = MixinPatchHelper(target)
        else:
            self.helper = target

        self.entry_branch = None
        self.offset2branch = {}

    def calculate_data_flow(self):
        pass

    def calculate_branches(self):
        # self.helper.re_eval_instructions()
        self.offset2branch = defaultdict(lambda: Branch(self))
        pending_ops = {0}
        done = set()

        while pending_ops:
            op = pending_ops.pop()
            branch = self.offset2branch[op]

            if branch in done:
                continue

            # print("new branch")

            while True:
                # print(op, op // 2, len(self.helper.instruction_listing))

                instr: dis.Instruction = self.helper.instruction_listing[op // 2]
                branch.add_instruction(instr)

                if instr.is_jump_target:
                    branch.following_branches.add(self.offset2branch[op])
                    done.add(branch)
                    branch = self.offset2branch[op]
                    if branch in done:
                        break

                # print(instr)

                if instr.opcode in FLOW_INTERRUPT:
                    done.add(branch)
                    break

                if instr.opcode in FLOW_JUMP_CONDITIONAL_DIRECT:
                    done.add(branch)
                    new = instr.argval
                    # print("+", new)
                    pending_ops.add(new)
                    pending_ops.add(op + 1)
                    branch.following_branches.add(self.offset2branch[new])
                    branch.following_branches.add(self.offset2branch[op + 2])
                    break

                if instr.opcode in FLOW_JUMP_CONDITIONAL_OFFSET:
                    done.add(branch)
                    new = op + instr.argval
                    # print("+", new)
                    pending_ops.add(new)
                    pending_ops.add(op + 1)
                    branch.following_branches.add(self.offset2branch[new])
                    branch.following_branches.add(self.offset2branch[op + 2])
                    break

                if instr.opcode == 110:
                    done.add(branch)
                    new = op + instr.argval
                    # print("->", new)
                    pending_ops.add(new)
                    branch.following_branches.add(self.offset2branch[new])
                    break

                if instr.opcode == 113:
                    done.add(branch)
                    new = instr.argval
                    # print("->", new)
                    pending_ops.add(new)
                    branch.following_branches.add(self.offset2branch[new])
                    break

                op += 2

        self.entry_branch = self.offset2branch[0]

    # todo: add a way to reassemble the branches to a single method


# if __name__ == "__main__":
#     obj = ControlFlowAnalyser(ControlFlowAnalyser.calculate_branches)
#
#     for i, instr in enumerate(obj.helper.instruction_listing):
#         print(i, instr)
#
#     obj.calculate_branches()
#     print(obj)
