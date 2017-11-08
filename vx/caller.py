# coding=utf-8
"""
f_locals 居然是浅拷贝
"""
import sys

value = 3


def get_current_frame():
    try:
        1 / 0
    except Exception, e:
        type, value, traceback = sys.exc_info()
        return traceback.tb_frame.f_back


def g():
    frame = get_current_frame()
    print 'current function is: ', frame.f_code.co_name
    caller = frame.f_back
    print 'caller function is: ', caller.f_code.co_name
    print "caller's local namespace: ", caller.f_locals
    print "caller's global namespace: ", caller.f_globals.keys()
    caller.f_locals['a'][0] = 100
    caller.f_locals['b'] = 4


def f():
    frame = sys._getframe()
    a = [1, 2]
    b = 2
    print "before call g()!f locals is:", frame.f_locals
    g()
    print "after call g()!f locals is:", frame.f_locals


def show():
    f()

show()
