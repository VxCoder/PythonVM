# coding=utf-8
"""
f_locals 居然是浅拷贝
"""
import sys


def g():

    frame = sys._getframe()
    caller = frame.f_back
    print "caller's local namespace: ", caller.f_locals
    caller.f_locals['a'][0] = 100
    caller.f_locals['b'] = 4
    caller.f_builtins['list'] = tuple


def f():
    a = [1, 2]
    b = 2
    print "before call g()!a = {}, b={}".format(a, b)
    g()
    print "after call g()!a = {}, b={}".format(a, b)
    c = list([3, 4])
    print c


f()

if __name__ == "__main__":
    f()
