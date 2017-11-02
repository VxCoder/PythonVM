# coding=utf-8
import os
import sys
import imp
import time
import struct
import tkinter.filedialog as filedialog

from Tkinter import *
from tkMessageBox import *
from ttk import *

from PyCode import PyCodeInfo
from RunPyc import PythonVM

MAGIC2VERSION = {
    20121: 'Python 1.5/1.5.1/1.5.2',
    50428: 'Python 1.6',
    50823: 'Python 2.0/2.0.1',
    60202: 'Python 2.1/2.1.1/2.1.2',
    60717: 'Python 2.2',
    62011: 'Python 2.3a0',
    62021: 'Python 2.3a0',
    62041: 'Python 2.4a0',
    62051: 'Python 2.4a3',
    62061: 'Python 2.4b1',
    62071: 'Python 2.5a0',
    62081: 'Python 2.5a0 (ast-branch)',
    62091: 'Python 2.5a0 (with)',
    62092: 'Python 2.5a0 (changed WITH_CLEANUP opcode)',
    62101: 'Python 2.5b3 (fix wrong code: for x, in ...)',
    62111: 'Python 2.5b3 (fix wrong code: x += yield)',
    62121: 'Python 2.5c1 (fix wrong lnotab with for loops and storing constants that should have been removed)',
    62131: 'Python 2.5c2 (fix wrong code: for x, in ... in listcomp/genexp)',
    62151: 'Python 2.6a0 (peephole optimizations and STORE_MAP opcode)',
    62161: 'Python 2.6a1 (WITH_CLEANUP optimization)',
    62171: 'Python 2.7a0 (optimize list comprehensions/change LIST_APPEND)',
    62181: 'Python 2.7a0 (optimize conditional branches:introduce POP_JUMP_IF_FALSE and POP_JUMP_IF_TRUE)',
    62191: 'Python 2.7a0 (introduce SETUP_WITH)',
    62201: 'Python 2.7a0 (introduce BUILD_SET)',
    62211: 'Python 2.7a0 (introduce MAP_ADD and SET_ADD)',
}


class PycParser(object):
    MAGIC_SLICE = slice(2)       # pyc 文件的魔数
    MTIME_SLICE = slice(4, 8)    # pyc 文件的创建时间

    def __init__(self, pyc_path):
        self.pyc_path = pyc_path
        self.internedStringList = []

    def read_long(self):
        data = struct.unpack("<I", self.pyc_data[:4])[0]
        self.pyc_data = self.pyc_data[4:]
        return data

    def read_string(self, strlen):
        string = struct.unpack("<{}s".format(strlen), self.pyc_data[:strlen])[0]
        self.pyc_data = self.pyc_data[strlen:]
        return string

    def read_NULL_type(self):
        return None

    def read_NONE_type(self):
        return None

    def read_FALSE_type(self):
        return False

    def read_TRUE_type(self):
        return True

    def read_INT_type(self):
        int_data = self.read_long()
        return int_data

    def read_STRING_type(self):
        strlen = self.read_long()
        string = struct.unpack("<{}s".format(strlen), self.pyc_data[:strlen])[0]
        self.pyc_data = self.pyc_data[strlen:]
        return string

    def read_UNICODE_type(self):
        string = self.read_STRING_type()
        return string

    def read_STRINGREF_type(self):
        stringref = self.read_long()
        string = self.internedStringList[stringref]
        return string

    def read_INTERNED_type(self):
        string = self.read_STRING_type()
        self.internedStringList.append(string)
        return string

    def read_TUPLE_type(self):
        tuplelen = self.read_long()
        tuple_data = tuple([self.read_object() for _ in range(tuplelen)])
        return tuple_data

    def read_LIST_type(self):
        listlen = self.read_long()
        list_data = [self.read_object() for _ in range(listlen)]
        return list_data

    def read_CODE_type(self):
        pycode_object = PyCodeInfo()
        pycode_object.co_argcount = self.read_long()
        pycode_object.co_nlocals = self.read_long()
        pycode_object.co_stacksize = self.read_long()
        pycode_object.co_flags = self.read_long()
        pycode_object.co_code = self.read_object()
        pycode_object.co_consts = self.read_object()
        pycode_object.co_names = self.read_object()
        pycode_object.co_varnames = self.read_object()
        pycode_object.co_freevars = self.read_object()
        pycode_object.co_cellvars = self.read_object()
        pycode_object.co_filename = self.read_object()
        pycode_object.co_name = self.read_object()
        pycode_object.co_firstlineno = self.read_long()
        pycode_object.co_lnotab = self.read_object()

        return pycode_object

    PY_TYPE_MAP = {
        # TYPE_STOPITER           'S'-
        # TYPE_ELLIPSIS           '.'-
        # TYPE_INT64              'I'-
        # TYPE_FLOAT              'f'-
        # TYPE_BINARY_FLOAT       'g'-
        # TYPE_COMPLEX            'x'-
        # TYPE_BINARY_COMPLEX     'y'-
        # TYPE_LONG               'l'-
        # TYPE_DICT               '{'-
        # TYPE_UNKNOWN            '?'-
        # TYPE_SET                '<'-
        # TYPE_FROZENSET          '>'-
        '0': read_NULL_type,
        'N': read_NONE_type,
        'F': read_FALSE_type,
        'T': read_TRUE_type,
        'i': read_INT_type,
        'c': read_CODE_type,
        't': read_INTERNED_type,
        's': read_STRING_type,
        '(': read_TUPLE_type,
        '[': read_LIST_type,
        'R': read_STRINGREF_type,
        'u': read_UNICODE_type,
    }

    def read_object(self):
        object_type = self.pyc_data[0]

        read_func = self.PY_TYPE_MAP.get(object_type, None)
        if not read_func:
            print("unknow type {}".format(object_type))
            sys.exit(2)

        self.pyc_data = self.pyc_data[1:]
        return read_func(self)

    def insign(self):

        self.pyc_data = None
        try:
            with open(self.pyc_path, 'rb') as fp:
                self.pyc_data = memoryview(fp.read())
        except IOError:
            print("{} file not find\n".format(self.pyc_path))

        except Exception as error:
            print(type(error), error.message)

        if not self.pyc_data:
            sys.exit(1)
            return

        magic = struct.unpack("<H", self.pyc_data[self.MAGIC_SLICE])[0]
        mtime = struct.unpack("<I", self.pyc_data[self.MTIME_SLICE])[0]
        self.pyc_data = self.pyc_data[self.MTIME_SLICE.stop:]

        pycode_object = self.read_object()
        pycode_object.version = MAGIC2VERSION.get(magic, 'unknow version')
        pycode_object.mtime = mtime

        return pycode_object


class PycShowApplication(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.parent = None
        self.pack()
        self.create_widgets()

    def create_widgets(self):

        label = Label(text='PYC结构').pack(side='top', fill='x')
        self.show_tree = Treeview()
        self.show_tree.pack(expand=True, fill='both', after=label)

        bottom = Frame()
        Button(bottom, text="打开PY文件", command=self.open_py).pack(side="left", expand=True)
        Button(bottom, text="打开PYC文件", command=self.open_pyc).pack(side="left", expand=True)
        self.run_button = Button(bottom, text="运行代码", state="disable", command=self.run_code)
        self.run_button.pack(side="left", expand=True)
        bottom.pack(side="bottom", fill="x")

    def insert_params(self, parent, text, note):
        return self.show_tree.insert(parent, 'end', text="{:<30}{}".format(text, note))

    def show_pyc_code(self, pycode_object, parent_id=''):
        show_tree = self.show_tree
        if not parent_id:
            parent = show_tree.insert(parent_id, 0, text=pycode_object.co_filename, open=True)
            show_tree.insert(parent, 'end', text="版本信息:{}".format(pycode_object.version))
            show_tree.insert(parent, 'end', text="修改时间:{}".format(time.ctime(pycode_object.mtime)))
            self.parent = parent
        else:
            parent = show_tree.insert(parent_id, 0, text=pycode_object.co_name, open=False)

        tmp_id = self.insert_params(parent, "co_argcount", "入参个数,不包括*args")
        show_tree.insert(tmp_id, 'end', '', text="value\t\t{}".format(pycode_object.co_argcount))

        tmp_id = self.insert_params(parent, "co_nlocals", "所有局部变量的个数,包括入参")
        show_tree.insert(tmp_id, 'end', text="value\t\t{}".format(pycode_object.co_nlocals))

        tmp_id = self.insert_params(parent, "co_stacksize", "需要的栈空间大小")
        show_tree.insert(tmp_id, 'end', text="value\t\t{}".format(pycode_object.co_stacksize))

        tmp_id = self.insert_params(parent, "co_flags", "各类标志")
        show_tree.insert(tmp_id, 'end', text="value\t\t{}".format(hex(pycode_object.co_flags)))

        tmp_id = self.insert_params(parent, "co_firstlineno", "代码块在对应源文件中的起始行")
        show_tree.insert(tmp_id, 'end', text="value\t\t{}".format(pycode_object.co_firstlineno))

        tmp_id = self.insert_params(parent, "co_filename", "完整源文件路径名")
        show_tree.insert(tmp_id, 'end', text="value\t\t{}".format(pycode_object.co_filename))

        tmp_id = self.insert_params(parent, "co_consts", "所有常量数据(所包含的代码块数据也在其中)")
        for const_item in pycode_object.co_consts:
            if isinstance(const_item, PyCodeInfo):
                self.show_pyc_code(const_item, tmp_id)
            elif isinstance(const_item, (str, int, tuple)):
                show_tree.insert(tmp_id, 'end', text=str(const_item))
            elif type(const_item) == bytes:
                show_tree.insert(tmp_id, 'end', text=const_item)
            elif const_item == None:
                show_tree.insert(tmp_id, 'end', text='None')
            else:
                print(const_item)

        tmp_id = self.insert_params(parent, "co_names", "所有变量名")
        for name in pycode_object.co_names:
            show_tree.insert(tmp_id, 'end', text=name)

        tmp_id = self.insert_params(parent, "co_varnames", "约束变量 -本代码段中被赋值，但没有被内层代码段引用的变量")
        for name in pycode_object.co_varnames:
            show_tree.insert(tmp_id, 'end', text=name)

        tmp_id = self.insert_params(parent, "co_cellvars", "内层约束变量 -本代码段中被赋值，且被内层代码段引用的变量")
        for name in pycode_object.co_cellvars:
            show_tree.insert(tmp_id, 'end', text=name)

        tmp_id = self.insert_params(parent, "co_freevars", "自由变量- 本代码段中被引用，在外层代码段中被赋值的变量")
        for name in pycode_object.co_freevars:
            show_tree.insert(tmp_id, 'end', text=name)

        self.insert_params(parent, "co_code", "字节码指令")
        self.insert_params(parent, "co_lnotab", "字节码指令与源代码行号对应关系")

    def generate_pyc(self, py_name):
        pyc_name = None
        fp = None
        try:
            real_name = os.path.basename(py_name.split('.')[0])
            fp, pathname, description = imp.find_module(real_name)
            imp.load_module(py_name, fp, pathname, description)
            pyc_name = real_name + '.pyc'
        except ImportError as error:
            showerror("错误信息", "{} 生成 pyc 文件失败 {}".format(py_name, error))
        except Exception as error:
            showerror("错误信息", "{}".format(error))

        return pyc_name

    def show_pyc(self, pyc_path):
        self.pycode_object = PycParser(pyc_path).insign()
        if self.parent:
            self.show_tree.delete(self.parent)
            self.parent = None
        self.run_button['state'] = 'normal'
        self.show_pyc_code(self.pycode_object)

    def open_py(self):
        py_path = filedialog.askopenfilename()
        if not py_path:
            return
        py_path = py_path.encode()
        pyc_path = self.generate_pyc(py_path)
        self.show_pyc(pyc_path)

    def open_pyc(self):
        pyc_path = filedialog.askopenfilename()
        if not pyc_path:
            return
        pyc_path = pyc_path.encode()
        self.show_pyc(pyc_path)

    def run_code(self):
        PythonVM(self.pycode_object).run()


def main():
    root = Tk()
    root.title("Pyc Insight")
    root.geometry('600x400')
    root.resizable(width=True, height=False)
    app = PycShowApplication(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
