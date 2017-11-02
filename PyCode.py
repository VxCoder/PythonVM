# coding=utf-8
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
