import builtins
import dis
import typing

from .PyBytecodeManipulator import FunctionPatcher
from .MixinMethodWrapper import MixinPatchHelper


class StackAnalyser:
    """
    Code for statically analyzing the stack of a MixinPatchHelper wrapper object
    """

    def __init__(self, patcher: MixinPatchHelper):
        self.patcher = patcher
        self.opcode2stack: typing.List[typing.Tuple[list, list, dict]] = []
        self.possible_return_values = []
        self.possible_yielded_values = []

    def prepareSimpleStack(self):
        self.opcode2stack.clear()
        self.possible_return_values.clear()
        self.possible_yielded_values.clear()

        self.opcode2stack = [None] * len(self.patcher.instruction_listing)

        visited_nodes = set()
        self.visitCp(0, visited_nodes, [], [None] * self.patcher.patcher.number_of_locals, {})

    def visitCp(self, cp: int, visited: typing.Set[int], stack: list, local: list, named_locals: dict):
        if cp in visited: return
        visited.add(cp)
        self.opcode2stack[cp] = stack.copy(), local.copy(), named_locals.copy()

        instr: dis.Instruction = self.patcher.instruction_listing[cp]

        if instr.opname in {"END_ASYNC_FOR", "BEFORE_ASYNC_WITH", "SETUP_ASYNC_WITH", "WITH_EXCEPT_START",
                            "UNPACK_SEQUENCE", "UNPACK_EX", "COMPARE_OP", "RAISE_VARARGS"}:
            return

        if instr.opname == "RETURN_VALUE":
            self.possible_return_values.append(stack.pop(-1))
            return

        # Instructions changing mostly nothing
        if instr.opname in ("NOP", "UNARY_POSITIVE", "UNARY_NEGATIVE", "UNARY_NOT", "UNARY_INVERT", "SETUP_ANNOTATIONS",
                            "POP_BLOCK", "POP_EXCEPT", "RERAISE", "LIST_TO_TUPLE", "SETUP_FINALLY"):
            return self.visitCp(cp+1, visited, stack, local, named_locals)

        # Instructions modifying the big stuff on the stack
        if instr.opname in {"GET_ITER", "GET_YIELD_FROM_ITER", "GET_AWAITABLE", "GET_AITER", "GET_ANEXT", "SETUP_WITH",
                            "GET_LEN", "MATCH_MAPPING", "MATCH_SEQUENCE", "MATCH_KEYS", "IMPORT_FROM"}:
            stack.pop(-1)
            stack.append(None)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname in {"POP_TOP", "BINARY_POWER", "BINARY_MULTIPLY", "BINARY_MATRIX_MULTIPLY",
                            "BINARY_FLOOR_DIVIDE", "BINARY_TRUE_DIVIDE", "BINARY_MODULO",
                            "BINARY_ADD", "BINARY_SUBTRACT", "BINARY_SUBSCR", "BINARY_LSHIFT",
                            "BINARY_RSHIFT", "BINARY_AND", "BINARY_XOR", "BINARY_OR",
                            "INPLACE_POWER", "INPLACE_MULTIPLY", "INPLACE_MATRIX_MULTIPLY",
                            "INPLACE_FLOOR_DIVIDE", "INPLACE_TRUE_DIVIDE", "INPLACE_MODULO",
                            "INPLACE_ADD", "INPLACE_SUBTRACT", "INPLACE_LSHIFT", "INPLACE_RSHIFT",
                            "INPLACE_AND", "INPLACE_XOR", "INPLACE_OR", "PRINT_EXPR", "SET_ADD",
                            "LIST_APPEND", "IMPORT_STAR", "COPY_DICT_WITHOUT_KEYS", "DELETE_ATTR",
                            "STORE_GLOBAL", "DELETE_GLOBAL", "LIST_EXTEND", "SET_UPDATE", "DICT_UPDATE",
                            "DICT_MERGE", "LOAD_ATTR", "IS_OP", "CONTAINS_OP"}:
            stack.pop(-1)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname in ("DELETE_SUBSCR", "MAP_ADD", "STORE_ATTR"):
            del stack[-2:]
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "IMPORT_NAME":
            del stack[-2:]
            stack.append(None)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "STORE_SUBSCR":
            del stack[-3:]
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "ROT_TWO":
            a, b = stack.pop(-1), stack.pop(-1)
            stack += a, b
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "ROT_THREE":
            a, b, c = stack.pop(-1), stack.pop(-1), stack.pop(-1)
            stack += a, c, b
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "ROT_FOUR":
            a, b, c, d = stack.pop(-1), stack.pop(-1), stack.pop(-1), stack.pop(-1)
            stack += a, d, c, b
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "DUP_TOP":
            a = stack[-1]
            stack.append(a)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "DUP_TOP_TWO":
            a = stack[-2:]
            stack.extend(a)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname in ("YIELD_VALUE", "YIELD_FROM"):
            self.possible_yielded_values.append(stack.pop(-1))
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "LOAD_ASSERTION_ERROR":
            stack.append(AssertionError)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname in ("LOAD_BUILD_CLASS", "LOAD_GLOBAL"):
            stack.append(None)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "STORE_NAME":
            named_locals[instr.argval] = stack.pop(-1)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "LOAD_NAME":
            stack.append(named_locals[instr.argval])
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "DELETE_NAME":
            del named_locals[instr.argval]
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "LOAD_CONST":
            stack.append(instr.argval)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "BUILD_TUPLE":
            stack.append(tuple(stack.pop(-1) for _ in range(instr.arg)))
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "BUILD_LIST":
            stack.append(list(stack.pop(-1) for _ in range(instr.arg)))
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "BUILD_SET":
            stack.append(set(stack.pop(-1) for _ in range(instr.arg)))
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "BUILD_DICT":
            stack.append({stack.pop(-2): stack.pop(-1) for _ in range(instr.arg)})
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "BUILD_CONST_KEY_MAP":
            keys = stack.pop(-1)
            stack.append({keys[i]: stack.pop(-1) for i in range(instr.arg)})
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "BUILD_STRING":
            del stack[-instr.arg:]
            stack.append(None)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "JUMP_FORWARD":
            return self.visitCp(cp + instr.argval, visited, stack, local, named_locals)

        if instr.opname in ("POP_JUMP_IF_TRUE", "POP_JUMP_IF_FALSE"):
            stack.pop(-1)
            self.visitCp(instr.argval, visited, stack.copy(), local.copy(), named_locals.copy())
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "JUMP_IF_NOT_EXC_MATCH":
            del stack[-2:]
            self.visitCp(instr.argval, visited, stack.copy(), local.copy(), named_locals.copy())
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname in ("JUMP_IF_TRUE_OR_POP", "JUMP_IF_FALSE_OR_POP"):
            self.visitCp(instr.argval, visited, stack.copy(), local.copy(), named_locals.copy())
            stack.pop(-1)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "FOR_ITER":
            self.visitCp(cp + instr.argval, visited, stack.copy(), local.copy(), named_locals.copy())
            stack.pop(-1)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "JUMP_ABSOLUTE":
            return self.visitCp(instr.argval, visited, stack.copy(), local.copy(), named_locals.copy())

        if instr.opname == "LOAD_FAST":
            local[instr.arg] = stack.pop(-1)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "STORE_FAST":
            stack.append(local[instr.arg])
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "DELETE_FAST":
            local[instr.arg] = None
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname in ("LOAD_CLOSURE", "LOAD_CLASSDEREF", "STORE_DEREF", "DELETE_DREF"):
            return """
            index = instr.arg
            if index < len(self.patcher.patcher.cell_vars):
                stack.append(self.patcher.patcher.cell_vars[index])
            else:
                stack.append(self.patcher.patcher.free_vars[index-len(self.patcher.patcher.cell_vars)])

            return self.visitCp(cp + 1, visited, stack, local, named_locals)"""

        if instr.opname == "CALL_FUNCTION":
            del stack[-(instr.arg+1):]
            stack.append(None)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

        if instr.opname == "CALL_FUNCTION_KW":
            del stack[-(instr.arg+2):]
            stack.append(None)
            return self.visitCp(cp + 1, visited, stack, local, named_locals)

