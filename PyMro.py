# coding:utf-8
# c3算法解决问题：
# 1.继承的单调性
# 2.菱形继承的方法覆盖

inherits = [
    """
O
F O
E O
D O
C F D
B D E
A B C
""",
    """
O
F O
E F
A E F
""",
]


def create_dict(lines):
    inherit_dict = {}
    for line in lines.split('\n'):
        line = line.strip()
        if not line:
            continue
        inherit_dict.update({line.split()[0]: line.split()[1:]})
    return inherit_dict


def print_mro(cls):
    for base in cls.__mro__[:-1]:
        print base.__name__,
    print ''


def create_classs(entry, inherit, class_infos=None):
    """
    python 的继承模式
    """
    bases = []
    class_infos = class_infos if class_infos != None else {}

    if entry in class_infos:
        return class_infos[entry]

    for base in inherit[entry]:
        if base not in class_infos:
            create_classs(base, inherit, class_infos)

        bases.append(class_infos[base])

    entry_class = class_infos[entry] = type(entry, tuple(bases), {})

    return entry_class


def merge(Lns, inherit):

    def head(lst):
        return lst[0]

    def tail(lst):
        return lst[1:]

    lst = []

    index = 0
    while len(Lns):
        if index >= len(Lns):
            raise TypeError("Cannot create a consistent method resolution")

        h = head(Lns[index])

        # 如果当前头在其他继承链的尾部,说明存在一个菱形继承,那采用广度搜索
        for i, Ln in enumerate(Lns):
            if i == index:
                continue

            # 这就是实现广度搜索的关键一步
            if h in tail(Ln):
                index += 1
                break
        else:
            new_Lns = []
            for Ln in Lns:
                if h != head(Ln):
                    new_Lns.append(Ln)
                    continue
                if tail(Ln):
                    new_Lns.append(tail(Ln))

            Lns = new_Lns
            lst.append(h)
            index = 0

    return lst


def L(C, inherit):
    """
    @ 我实现的C3算法
    """
    lst = [C]

    if len(inherit[C]):
        # 通过递归实现深度搜索, 从而保证单调性
        Lns = [L(base, inherit) for base in inherit[C]]
        Lns.append(inherit[C])

        # 通过merge算法,实现菱形继承时,方法不能覆盖问题
        lst += merge(Lns, inherit)

    return lst


def main():
    for inherit in inherits:
        inherit_dict = create_dict(inherit)
        print_mro(create_classs("A", inherit_dict))
        print(" ".join(L("A", inherit_dict)))


if __name__ == "__main__":
    main()
