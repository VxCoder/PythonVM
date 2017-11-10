# coding=utf-8

from collections import namedtuple


class PyTraceback(object):

    def __init__(self, next, frame):
        self.tb_next = next
        self.tb_frame = frame
        self.tb_lasti = frame.f_lasti
        self.tb_lineno = self.get_line_number(frame)

    def get_line_number(self, frame):
        return self.addr2line(frame.f_code, frame.f_lasti)

    def addr2line(self, code, lasti):
        size = len(code.co_lnotab)
        line = code.co_firstlineno
        lnotab = code.co_lnotab
        index = 0
        addr = 0

        while index < size:
            addr += ord(lnotab[index])
            if addr > lasti:
                break
            line += ord(lnotab[index + 1])
            index += 2

        return line


class PyThreadState(object):

    """
    PyThreadState 类似于线程
    """

    def __init__(self):
        self.frame = None
        self.curexc_type = None  # 异常类型
        self.curexc_value = None  # 异常值
        self.curexc_traceback = None  # 异常回溯

    def fetch_error(self):
        curexc_type = self.curexc_type
        curexc_value = self.curexc_value
        curexc_traceback = self.curexc_traceback

        self.curexc_type = None
        self.curexc_value = None
        self.curexc_traceback = None

        return curexc_type, curexc_value, curexc_traceback

    def store_error(self, curexc_type, curexc_value, curexc_traceback=None):
        self.curexc_type = curexc_type
        self.curexc_value = curexc_value


class PyFunctionObject(object):

    def __init__(self, code, globals):
        self.func_code = code  # 运行代码
        self.func_globals = globals  # 全局变量
        self.func_name = code.co_name  # 函数名
        self.func_defaults = []  # 默认参数
        self.func_closure = None

    def set_closure(self, cells):
        self.func_closure = cells


PyBlock = namedtuple("PyBlock", "b_type, b_handler, b_level")


class PyCellObject(object):

    def __init__(self, *args):
        if len(args):
            self.ob_ref = args[0]

    def set(self, obj):
        self.ob_ref = obj

    def get(self):
        return self.ob_ref  # 获取前,应该已经设置过了


class PyFrameObject(object):
    """
    python 运行栈对象
    f_back:          前一个运行栈
    f_code:          代码段
    f_builtins:      内建命名空间
    f_globals:       全局命名空间
    f_locals:        局部命名空间
    f_stack:         运行时栈
    f_lasti:         最后执行的代码地址
    block_stack:     代码block对象
    """

    def __init__(self, thread_state, f_code, f_globals, f_locals):
        self.f_back = thread_state.frame  # 之前的运行栈

        self.f_code = f_code              # 运行代码

        self.f_locals = f_locals          # 局部命名空间
        self.f_globals = f_globals        # 全局命名空间
        self.f_builtins = None            # 内建命名空间

        if self.f_back == None:

            self.f_builtins = __builtins__
        else:
            self.f_builtins = self.f_back.f_builtins

        self.f_stack = []
        self.f_lasti = -1

        # 静态局部变量保存地方
        # CO_OPTIMIZED | CO_NEWLOCALS 生效时，LOAD|STORE_FAST 使用
        extras = f_code.co_nlocals + len(f_code.co_cellvars) + len(f_code.co_freevars)
        self.f_fast_local = [None for _ in range(extras)]

        self.block_stack = []  # 代码块


class PyCodeObject(object):

    CO_OPTIMIZED = 0x0001   # 局部变量快速读取
    CO_NEWLOCALS = 0x0002   # 局部变量快速读取
    CO_VARARGS = 0x0004  # 扩展位置参数
    CO_VARKEYWORDS = 0x0008  # 扩展键参数
    CO_NESTED = 0x0010  # 闭包函数标志
    CO_GENERATOR = 0x0020  # 生成器
    CO_NOFREE = 0x0040  # 没有闭包

    def __init__(self):
        self.co_co_argcount = None
        self.co_nlocals = None
        self.co_stacksize = None
        self.co_flags = None
        self.co_code = None
        self.co_consts = None
        self.co_names = None
        self.co_varnames = None
        self.co_freevars = None
        self.co_cellvars = None
        self.co_filename = None
        self.co_name = None
        self.co_firstlineno = None
        self.co_lnotab = None
        self.version = None
        self.mtime = None
