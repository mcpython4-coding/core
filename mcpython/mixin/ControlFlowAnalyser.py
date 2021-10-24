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
        self.instructions = []

        self.batch = None
        self.rendering_objects = []

    def add_instruction(self, instr: dis.Instruction):
        self.instructions.append(instr)
        return self

    def prepare_rendering(self):
        self.batch = pyglet.graphics.Batch()

    def draw(self):
        self.batch.draw()


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

    # todo: add a way to reassemble the branches to a single method


if __name__ == "__main__":
    obj = ControlFlowAnalyser(ControlFlowAnalyser.calculate_branches)

    for i, instr in enumerate(obj.helper.instruction_listing):
        print(i, instr)

    obj.calculate_branches()
    print(obj)
