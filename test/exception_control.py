try:
    1 / 0
except Exception:
    pass
finally:
    print 'the finally code'

print 'hello'


def hello():
    1 / 0


def world():
    hello()


def foo():
    world()


def bar():
    foo()
bar()
