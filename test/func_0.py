def f():
    print 'in f'


def g():
    print 'in g'
    f()


def h():
    print 'in h'
    g()

h()
