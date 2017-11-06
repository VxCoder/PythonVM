# coding=utf-8

from collections import namedtuple

class PyThreadState(object):

    """
    PyThreadState 类似于线程
    """

    def __init__(self):
        self.frame = None

PyBlock = namedtuple("PyBlock", "b_type, b_handler, b_level")

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
    block_stack:     代码block对象
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
        
        self.block_stack = [] #代码块
             
class PyCodeInfo(object):

    def __init__(self):
        self.__dict__ = {key: None for key in ('co_argcount', 'co_nlocals', 'co_stacksize',
                                               'co_flags', 'co_code', 'co_consts', 'co_names',
                                               'co_varnames', 'co_freevars', 'co_cellvars',
                                               'co_filename', 'co_name', 'co_firstlineno', 'co_lnotab',
                                               'version', 'mtime')}

    def __str__(self):
        return "\n*************************\n"\
            "CodeOjbect:{co_name}\n"\
            "co_argcount:{co_argcount}\n"\
            "co_nlocals:{co_nlocals}\n"\
            "co_stacksize:{co_stacksize}\n"\
            "co_flags:{co_flags}\n"\
            "co_names:{co_names}\n"\
            "co_consts:{co_consts}\n"\
            "co_filename:{co_filename}\n"\
            "*************************\n".format(**self.__dict__)

    __repr__ = __str__

