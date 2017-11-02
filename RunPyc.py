# coding=utf-8
class PyThreadState(object):

    def __init__(self):
        pass


class PyFrame(object):
    """
    python 运行栈对象
    f_back:          前一个运行栈
    f_code:          代码端
    f_builtins:      内建命名空间
    f_globals:       全局命名空间
    f_loclas:        局部命名空间
    f_valuestack:    指向最后一个局部变量地址后面，运行时栈底地址
    f_stacktop:      运行栈顶地址
    f_lasti:         最后执行指令地址
    f_lineno:        当前行
    f_localsplus:    局部变量+栈空间
    f_trace/f_exc_type/f_exc_value/f_exc_traceback： 异常跟踪
    """

    def __init__(self, thread_state, code, globals, loclas):
        self.f_back = thread_state.frame  # 之前的运行栈
        self.f_code = f_code              # 运行代码
        self.f_builtins = None            # 内建命名空间
        self.f_globals = f_globals        # 全局命名空间
        self.f_loclas = f_locals          # 局部命名空间

        if(self.f_back == None or self.f_back.f_globals != globals):
            self.f_builtins = f_locals['__builtins__']
        else:
            self.f_builtins = self.f_back.f_builtins


class PythonVM(object):

    def __init__(self, pycode_object):
        self.pycode_object = pycode_object

    def run_code(self):
        print("hello")
