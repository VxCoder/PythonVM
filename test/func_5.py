def foo():
    for i in [1, 2, 3]:
        yield i

bar = foo()
# print next(bar)
