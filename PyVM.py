# coding=utf-8
import sys
import operator
import traceback

import OpCode
from PyObject import PyThreadState, PyFunction, PyFrame, PyBlock, PyTraceback


class PythonVM(object):
    """
    PythonVM 类似于CPU,执行code,切换运行时frame
    """

    WHY_NOT = None  # No error
    WHY_EXCEPTION = 0x0002  # Exception occurred
    WHY_RERAISE = 0x0004  # Exception re-raised by 'finally'
    WHY_RETURN = 0x0008  # 'return' statement
    WHY_BREAK = 0x0010  # 'break' statement
    WHY_CONTINUE = 0x0020  # 'continue' statement
    WHY_YIELD = 0x0040  # 'yield' operator

    TYPE_SETUP_LOOP = 'loop'
    TYPE_SETUP_FINALLY = 'finally'
    TYPE_SETUP_EXCEPT = 'except'

    def __init__(self, pycode_object, outstream, source_file=None):
        self.pycode_object = pycode_object
        self.outstream = outstream
        self.source_file = source_file
        self.thread_state = PyThreadState()

    def get_thread_state(self):
        return self.thread_state

    def run_code(self, globals=None):

        globals = globals or {}  # 最外层的Frame,globals == locals

        frame = PyFrame(thread_state=self.get_thread_state(),
                        f_code=self.pycode_object,
                        f_globals=globals,
                        f_locals=globals)

        why = self.eval_frame(frame, 0)

        if why == self.WHY_EXCEPTION:
            # 堆栈展开
            tstate = self.get_thread_state()

            error_type, error_value, error_tb = self.fetch_error()

            if self.source_file:
                fp = open(self.source_file)

            while error_tb:

                self.outstream('File "{}", line {}, in {}'.format(
                    error_tb.tb_frame.f_code.co_filename,
                    error_tb.tb_lineno,
                    error_tb.tb_frame.f_code.co_name))

                if self.source_file:
                    for _ in range(error_tb.tb_lineno):
                        line = fp.readline()
                    self.outstream('\t{}'.format(line.strip()))
                    fp.seek(0, 0)

                error_tb = error_tb.tb_next

            self.outstream("{}: {}".format(error_type, error_value))

    def fetch_error(self):
        return self.get_thread_state().fetch_error()

    def store_error(self, error_type, error_value):
        self.get_thread_state().store_error(error_type, error_value)

    def trace_back_here(self, frame):
        tstate = self.get_thread_state()

        oldtb = tstate.curexc_traceback
        tb = PyTraceback(oldtb, frame)
        tstate.curexc_traceback = tb

    def parse_code_and_args(self):
        co_code = self.frame.f_code.co_code
        f_lasti = self.frame.f_lasti

        arg = None

        code = ord(co_code[f_lasti])
        opname = OpCode.op_code[code]

        if OpCode.has_arg(code):
            arg = (ord(co_code[f_lasti + 2]) << 8) + ord(co_code[f_lasti + 1])
            self.frame.f_lasti += 3
        else:
            self.frame.f_lasti += 1

        return opname, arg

    def dispatch(self, opname, arg):
        why = None

        try:
            if opname.startswith('UNARY_'):
                self.unaryOperator(opname[6:])
            elif opname.startswith('BINARY_'):
                self.binaryOperator(opname[7:])
            elif opname.startswith('INPLACE_'):
                self.inplaceOperator(opname[8:])
            else:
                op_func = getattr(self, opname, None)

                if not op_func:
                    print "not support {} now".format(opname)
                else:
                    why = op_func(arg) if arg != None else op_func()

        except Exception:
            error_info = sys.exc_info()
            self.store_error(error_info[0], error_info[1])

            print traceback.print_tb(sys.exc_info()[2])
            why = self.WHY_EXCEPTION

        return why

    def eval_frame(self, frame, throwflag):
        self.get_thread_state().frame = frame

        self.frame = frame
        self.frame.f_lasti += 1

        while True:
            opname, arg = self.parse_code_and_args()

            why = self.dispatch(opname, arg)

            if why == self.WHY_NOT:
                continue

            if why == self.WHY_EXCEPTION:
                # 保存异常Frame,展开异常堆栈用
                self.trace_back_here(self.frame)

            if why == self.WHY_RERAISE:
                why = self.WHY_EXCEPTION

            while (why != self.WHY_NOT) and len(self.frame.block_stack):
                block = self.pop_block(self.frame)

                # 恢复到进入代码块前的堆栈状态
                while self.stack_level() > block.b_level:
                    self.pop()

                # 针对块内的break操作
                if block.b_type == self.TYPE_SETUP_LOOP and why == self.WHY_BREAK:
                    why = self.WHY_NOT
                    self.jumpto(block.b_handler)
                    break

                # 块内有异常发生
                if (block.b_type == self.TYPE_SETUP_FINALLY) or (block.b_type == self.TYPE_SETUP_EXCEPT and why == self.WHY_EXCEPTION):
                    if why == self.WHY_EXCEPTION:
                        exc, val, tb = self.fetch_error()
                        self.push(tb)
                        self.push(val)
                        self.push(exc)

                    why = self.WHY_NOT
                    self.jumpto(block.b_handler)
                    break

            if why != self.WHY_NOT:
                break

        self.get_thread_state().frame = frame.f_back
        return why

    def get_const(self, index):
        return self.frame.f_code.co_consts[index]

    def get_name(self, index):
        return self.frame.f_code.co_names[index]

    def top(self):
        return self.frame.f_stack[-1]

    def set_top(self, value):
        self.frame.f_stack[-1] = value

    def push(self, value):
        self.frame.f_stack.append(value)

    def pop(self):
        return self.frame.f_stack.pop()

    def popn(self, n):
        if n:
            ret = self.frame.f_stack[-n:]
            self.frame.f_stack[-n:] = []
            return ret
        else:
            return []

    def jumpto(self, dest):
        self.frame.f_lasti = dest

    def jumpby(self, dest):
        self.frame.f_lasti += dest

    def stack_level(self):
        return len(self.frame.f_stack)

    def setup_block(self, frame, b_type, b_handler, b_level):
        block = PyBlock(b_type, b_handler, b_level)
        frame.block_stack.append(block)

    def fast_function(self, func, stack, n, na, nk):
        co = func.func_code
        globals = func.func_globals
        argdefs = func.func_defaults

        if argdefs == None and co.co_argcount == n and nk == 0:
            frame = PyFrame(self.get_thread_state(), co, globals, None)
            retval = self.eval_frame(frame, 0)
            return retval

    def call_function(self, stack, oparg):
        na = oparg & 0xff
        nk = (oparg >> 8) & 0xff
        n = na + 2 * nk

        func = stack[-n - 1]

        x = self.fast_function(func, stack, n, na, nk)
        return x

    def pop_block(self, frame):
        return frame.block_stack.pop()

    def detail_print(self, name, *args):
        return
        print name

    UNARY_OPERATORS = {
        'POSITIVE': operator.pos,  # +a
        'NEGATIVE': operator.neg,  # -a
        'NOT':      operator.not_,  # not a
        'CONVERT':  repr,
        'INVERT':   operator.invert,  # ~ a
    }

    def unaryOperator(self, op):
        value = self.top()
        self.set_top(self.UNARY_OPERATORS[op](value))

    BINARY_OPERATORS = {
        'POWER':    pow,          # a**b
        'MULTIPLY': operator.mul,  # a * b
        'DIVIDE':   operator.div,  # a / b    __future__.division 没有生效
        'FLOOR_DIVIDE': operator.floordiv,  # a // b
        'TRUE_DIVIDE':  operator.truediv,  # a/b  __future__.division 生效
        'MODULO':   operator.mod,           # a % b
        'ADD':      operator.add,           # a + b
        'SUBTRACT': operator.sub,           # a - b
        'SUBSCR':   operator.getitem,       # a[b]
        'LSHIFT':   operator.lshift,        # a << b
        'RSHIFT':   operator.rshift,        # a >> b
        'AND':      operator.and_,          # a & b
        'XOR':      operator.xor,           # a ^ b
        'OR':       operator.or_,           # a | b
    }

    def binaryOperator(self, op):
        x, y = self.popn(2)
        self.push(self.BINARY_OPERATORS[op](x, y))

    def inplaceOperator(self, op):
        y = self.pop()
        x = self.top()
        self.set_top(self.BINARY_OPERATORS[op](x, y))

    COMPARE_OPERATORS = [
        operator.lt,
        operator.le,
        operator.eq,
        operator.ne,
        operator.gt,
        operator.ge,
        lambda x, y: x in y,
        lambda x, y: x not in y,
        lambda x, y: x is y,
        lambda x, y: x is not y,
        lambda x, y: issubclass(x, Exception) and issubclass(x, y),
    ]

    def COMPARE_OP(self, opnum):
        self.detail_print("COMPARE_OP")
        y = self.pop()
        x = self.top()
        self.set_top(self.COMPARE_OPERATORS[opnum](x, y))

        # cpython 会预测下条跳转指令, 这里不做类似优化了

    def POP_JUMP_IF_FALSE(self, addr):
        self.detail_print("POP_JUMP_IF_FALSE")

        value = self.pop()
        if not value:
            self.jumpto(addr)

    def POP_JUMP_IF_TRUE(self, addr):
        self.detail_print("POP_JUMP_IF_TRUE")

        val = self.pop()
        if val:
            self.jumpto(addr)

    def JUMP_FORWARD(self, addr):
        self.detail_print("JUMP_FORWARD")
        self.jumpby(addr)

    def SETUP_LOOP(self, dest):
        self.detail_print("SETUP_LOOP")
        self.setup_block(self.frame, self.TYPE_SETUP_LOOP, self.frame.f_lasti + dest,  self.stack_level())

    def SETUP_FINALLY(self, dest):
        self.detail_print("SETUP_FINALLY")
        self.setup_block(self.frame, self.TYPE_SETUP_FINALLY, self.frame.f_lasti + dest,  self.stack_level())

    def SETUP_EXCEPT(self, dest):
        self.detail_print("SETUP_EXCEPT")
        self.setup_block(self.frame, self.TYPE_SETUP_EXCEPT, self.frame.f_lasti + dest,  self.stack_level())

    # no test
    def RAISE_VARARGS(self, argc):
        self.detail_print("RAISE_VARARGS")

        exctype = None
        value = None
        tb = None

        if argc == 1:
            exctype = self.pop()
        elif argc == 2:
            value = self.pop()
            exctype = self.pop()
        elif argc == 3:
            tb = self.pop()
            value = self.pop()
            exctype = self.pop()
        elif argc != 0:
            print "!!!!!!"

        self.store_error(exctype, value, tb)

        return self.WHY_EXCEPTION

    def END_FINALLY(self):
        self.detail_print("END_FINALLY")
        v = self.pop()

        # 异常没有处理掉时，退出时重新抛出
        if v is None:
            return self.WHY_NOT
        elif issubclass(v, BaseException):
            val = self.pop()
            tb = self.pop()
            self.store_error(v, value, tb)

            return self.WHY_RERAISE

    def GET_ITER(self):
        self.detail_print("GET_ITER")

        value = self.top()
        value_iter = iter(value)
        if value_iter:
            self.set_top(value_iter)
        else:
            self.pop()

    def FOR_ITER(self, dest):
        self.detail_print("FOR_ITER")

        it = self.top()

        try:
            value = next(it)
            self.push(value)
        except StopIteration:
            self.pop()
            self.jumpby(dest)

    def POP_BLOCK(self):
        self.detail_print("POP_BLOCK")

        block = self.pop_block(self.frame)
        while self.stack_level() > block.b_level:
            self.pop()

    def BREAK_LOOP(self):
        self.detail_print("BREAK_LOOP")

        return self.WHY_BREAK

    def JUMP_ABSOLUTE(self, dest):
        self.detail_print("JUMP_ABSOLUTE")

        self.jumpto(dest)

    def POP_TOP(self):
        self.detail_print("POP_TOP")

        self.pop()

    def NOP(self):
        self.detail_print("NOP")

        pass

    def DUP_TOP(self):
        self.detail_print("DUP_TOP")
        self.push(self.top())

    def ROT_TWO(self):
        self.detail_print("ROT_TWO")

        a, b = self.popn(2)
        self.push(b, a)

    def ROT_THREE(self):
        self.detail_print("ROT_THREE")

        a, b, c = self.popn(3)
        self.push(c, a, b)

    def ROT_FOUR(self):
        self.detail_print("ROT_FOUR")

        a, b, c, d = self.popn(4)
        self.push(d, a, b, c)

    def LOAD_CONST(self, index):
        self.detail_print("LOAD_CONST")

        value = self.get_const(index)
        self.push(value)

    def STORE_NAME(self, index):
        self.detail_print("STORE_NAME")

        name = self.get_name(index)
        value = self.pop()
        self.frame.f_locals[name] = value

    def STORE_MAP(self):
        self.detail_print("STORE_MAP")

        map, val, key = self.popn(3)
        map[key] = val
        self.push(map)

    def STORE_SUBSCR(self):
        self.detail_print("STORE_SUBSCR")

        val, map, subscr = self.popn(3)
        map[subscr] = val

    def LOAD_NAME(self, index):
        self.detail_print("LOAD_NAME")

        name = self.get_name(index)
        frame = self.frame
        if name in frame.f_locals:
            value = frame.f_locals[name]
        elif name in frame.f_globals:
            value = frame.f_globals[name]
        elif name in frame.f_builtins:
            value = frame.f_builtins[name]
        else:
            raise NameError("name '%s' is not defined".foramt(name))
        self.push(value)

    def LOAD_GLOBAL(self, args):
        name = self.get_name(args)
        self.push(self.frame.f_globals[name])

    def BUILD_MAP(self, _):
        self.detail_print("BUILD_MAP")
        self.push({})

    def BUILD_TUPLE(self, num):
        value = self.popn(num)
        self.push(tuple(value))

    def BUILD_LIST(self, num):
        value = self.popn(num)
        self.push(value)

    def MAKE_FUNCTION(self, oparg):
        self.detail_print("MAKE_FUNCTION")

        code = self.pop()
        func = PyFunction(code, self.frame.f_globals)

        if func and oparg > 0:
            pass

        self.push(func)

    def CALL_FUNCTION(self, oparg):
        self.detail_print("CALL_FUNCTION")

        sp = self.frame.f_stack
        x = self.call_function(sp, oparg)
        self.frame = self.get_thread_state().frame

        self.push(x)
        return x

    def PRINT_ITEM(self):
        value = self.pop()
        self.outstream(value, False)

    def PRINT_NEWLINE(self):
        self.outstream('')

    def RETURN_VALUE(self):
        self.ret_value = self.pop()
        return self.WHY_RETURN
