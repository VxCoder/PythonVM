# coding=utf-8
import sys

import OpCode


class PyThreadState(object):
    """
    PyThreadState 类似于线程
    """

    def __init__(self):
        self.frame = None


class PyFrame(object):
    """
    python 运行栈对象
    f_back:          前一个运行栈
    f_code:          代码段
    f_builtins:      内建命名空间
    f_globals:       全局命名空间
    f_locals:        局部命名空间
    f_stack:         运行时栈
    f_lasti:         最后执行的代码地址
    """

    def __init__(self, thread_state, f_code, f_globals, f_locals):
        self.f_back = thread_state.frame  # 之前的运行栈

        self.f_code = f_code                # 运行代码

        self.f_locals = f_locals          # 局部命名空间
        self.f_globals = f_globals        # 全局命名空间
        self.f_builtins = None            # 内建命名空间

        if self.f_back == None:
            self.f_builtins = __builtins__
        else:
            self.f_builtins = self.f_back.f_builtins

        self.f_stack = []
        self.f_lasti = -1


class PythonVM(object):
    """
    PythonVM 类似于CPU,执行code,切换运行时frame
    """

    def __init__(self, pycode_object):
        self.pycode_object = pycode_object

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

        op_func = getattr(self, opname, None)
        if not op_func:
            print "not support {} now".format(opname)
            return

        return op_func(arg) if arg != None else op_func()

    def run_code(self):
        thread_state = PyThreadState()
        self.frame = PyFrame(thread_state=thread_state,
                             f_code=self.pycode_object,
                             f_globals={},
                             f_locals={})

        self.frame.f_lasti += 1
        while True:
            opname, arg = self.parse_code_and_args()
            result = self.dispatch(opname, arg)
            if result:
                print "return value:{}\n".format(result)
                break

    def get_const(self, index):
        return self.frame.f_code.co_consts[index]

    def get_name(self, index):
        return self.frame.f_code.co_names[index]

    def top(self):
        return self.frame.f_stack[-1]

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

    def DUP_TOP(self):
        self.push(self.top())

    def ROT_TWO(self):
        a, b = self.popn(2)
        self.push(b, a)

    def ROT_THREE(self):
        a, b, c = self.popn(3)
        self.push(c, a, b)

    def ROT_FOUR(self):
        a, b, c, d = self.popn(4)
        self.push(d, a, b, c)

    def LOAD_CONST(self, index):
        value = self.get_const(index)
        self.push(value)

    def STORE_NAME(self, index):
        name = self.get_name(index)
        value = self.pop()
        self.frame.f_locals[name] = value

    def STORE_MAP(self):
        map, val, key = self.popn(3)
        map[key] = val
        self.push(map)

    def STORE_SUBSCR(self):
        val, map, subscr = self.popn(3)
        map[subscr] = val

    def LOAD_NAME(self, index):
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

    def BUILD_MAP(self, _):
        self.push({})

    def BUILD_TUPLE(self, num):
        value = self.popn(num)
        self.push(tuple(value))

    def BUILD_LIST(self, num):
        value = self.popn(num)
        self.push(value)

    def PRINT_ITEM(self):
        value = self.pop()
        print value,

    def PRINT_NEWLINE(self):
        print ''

    def RETURN_VALUE(self):
        ret_value = self.pop()
        return str(ret_value)
