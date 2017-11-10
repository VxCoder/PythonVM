def get_func(arg):
    value = "inner"

    def inner_func():
        print arg
        print value

    return inner_func

show_value = get_func("params")
show_value()
