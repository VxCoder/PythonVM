def Py_Func(value, *lst, **keys):
    print value
    print lst
    print keys

Py_Func(-1, 1, 2, a=3, b=4)


def Test_Func(a,  b=1, *args, **kwargs):
    c = a + b
    print c


Test_Func(1, 2, 3, 4, c=1)
