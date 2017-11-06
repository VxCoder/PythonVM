# coding=utf-8
import os
import sys
import imp
import time
import marshal
import struct
import tkFont
import tkinter.filedialog as filedialog
from tkinter.scrolledtext import ScrolledText
from Tkinter import *
from tkMessageBox import *
from ttk import *


import OpCode
from PyObject import PyCodeInfo
from PyVM import PythonVM
import py_compile


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
        # 暂时处理4字节整数
        if int_data >> 31:
            int_data = - ((int_data ^ 0xffffffff) + 1)

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
        pycode_object.mtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mtime))

        return pycode_object


class PycShowApplication(Frame):

    def __init__(self, master=None):
        Frame.__init__(self, master)
 
        self.parent = None
        self.pack()
        self.create_widgets()

        py_path = "D:/Git/PythonVM/test/exception.py"
        pyc_path = self.generate_pyc(py_path)
        self.show_pyc(pyc_path, py_path)

    def set_style(self):
        self.background = "#272822"
        self.main_color = "#A7EC21"
        self.font = tkFont.Font(family='Helvetica', size=12, weight='bold')
        Style().configure("Treeview", background=self.background, foreground=self.main_color, font=self.font)
        Style().configure("TLabel", background=self.background, foreground="#52E3F6", font=self.font)

    def create_widgets(self):
        self.set_style()

        Label(text='PYC结构').pack(fill=X)

        show_frame = Frame()
        vbar = Scrollbar(show_frame)
        vbar.pack(side=RIGHT, fill=Y)

        self.show_tree = Treeview(show_frame)
        self.show_tree.pack(side=LEFT,  fill=BOTH, expand=True)

        self.show_tree['yscrollcommand'] = vbar.set
        vbar['command'] = self.show_tree.yview

        show_frame.pack(fill=BOTH, expand=True)

        bottom = Frame()
        Button(bottom, text="打开PY文件", command=self.open_py).pack(side=LEFT, expand=True)
        Button(bottom, text="打开PYC文件", command=self.open_pyc).pack(side=LEFT, expand=True)
        self.run_button = Button(bottom, text="运行代码", state="disable", command=self.run_code)
        self.run_button.pack(side=LEFT, expand=True)
        bottom.pack(fill=X)

    def insert_params(self, parent, text, note, tab=2, open=False):
        return self.show_tree.insert(parent, END, open=open, text="{}{}{}".format(text, '\t' * tab, note))

    def dis_code(self, pycode_object, show_tree, parent_id, co_code=None, last=None):
        last = last or 0
        co_code = co_code or memoryview(pycode_object.co_code)

        while co_code:
            code = ord(co_code[0])
            opname = OpCode.op_code[code]
            if OpCode.has_arg(code):
                index = (ord(co_code[2]) << 8) + ord(co_code[1])
                if code in OpCode.has_const():
                    arg = pycode_object.co_consts[index]
                elif code in OpCode.has_names():
                    arg = pycode_object.co_names[index]

                if len(opname) > 13:
                    outstr = "{}\t{}\t\t{}".format(last, opname, index)
                else:
                    outstr = "{}\t{}\t\t\t{}".format(last, opname, index)
                    
                if 'arg' in locals():
                    outstr += "\t({})".format(arg)
                    del arg

                last += 3
                co_code = co_code[3:]
            else:
                outstr = "{}\t{}".format(last, opname)
                last += 1
                co_code = co_code[1:]

            show_tree.insert(parent_id, END, text=outstr)

        return last

    def dis_code_with_source(self, pycode_object, show_tree, parent_id, filename):

        last = 0
        lineno = 1
        source = open(filename)
        lntoab = memoryview(pycode_object.co_lnotab)
        co_code = memoryview(pycode_object.co_code)

        for _ in xrange(pycode_object.co_firstlineno - 1):
            source.readline()
            lineno += 1

        while lntoab:
            code_offset = ord(lntoab[0])
            souce_offset = ord(lntoab[1])

            for _ in xrange(souce_offset):
                line = source.readline()
                if line.strip():
                    show_tree.insert(parent_id, END, text="*{}\t{}".format(lineno, line))
                lineno += 1

            last = self.dis_code(pycode_object, show_tree, parent_id, co_code=co_code[:code_offset], last=last)
            co_code = co_code[code_offset:]
            lntoab = lntoab[2:]

        for line in source:
            show_tree.insert(parent_id, END, text="*{}\t{}".format(lineno, line))
            lineno += 1
        self.dis_code(pycode_object, show_tree, parent_id, co_code=co_code, last=last)

        source.close()

    def show_pyc_code(self, pycode_object, parent_id='', py_path=None):
        show_tree = self.show_tree
        if not parent_id:
            parent = show_tree.insert(parent_id, 0, text=pycode_object.co_filename, open=True)
            self.insert_params(parent, "版本信息", pycode_object.version, tab=3)
            self.insert_params(parent, "修改时间", pycode_object.mtime, tab=3)
            self.parent = parent
        else:
            parent = show_tree.insert(parent_id, 0, text=pycode_object.co_name, open=False)

        tmp_id = self.insert_params(parent, "co_argcount", "入参个数,不包括*args")
        show_tree.insert(tmp_id, END, text="value\t\t{}".format(pycode_object.co_argcount))

        tmp_id = self.insert_params(parent, "co_nlocals", "所有局部变量的个数,包括入参")
        show_tree.insert(tmp_id, END, text="value\t\t{}".format(pycode_object.co_nlocals))

        tmp_id = self.insert_params(parent, "co_stacksize", "需要的栈空间大小")
        show_tree.insert(tmp_id, END, text="value\t\t{}".format(pycode_object.co_stacksize))

        tmp_id = self.insert_params(parent, "co_flags", "各类标志", tab=3)
        show_tree.insert(tmp_id, END, text="value\t\t{}".format(hex(pycode_object.co_flags)))

        tmp_id = self.insert_params(parent, "co_firstlineno", "代码块在对应源文件中的起始行")
        show_tree.insert(tmp_id, END, text="value\t\t{}".format(pycode_object.co_firstlineno))

        tmp_id = self.insert_params(parent, "co_filename", "完整源文件路径名")
        show_tree.insert(tmp_id, END, text="value\t\t{}".format(pycode_object.co_filename))

        tmp_id = self.insert_params(parent, "co_consts", "所有常量数据(所包含的代码块数据也在其中)")
        for const_item in pycode_object.co_consts:
            if isinstance(const_item, PyCodeInfo):
                self.show_pyc_code(const_item, tmp_id, py_path)
            elif isinstance(const_item, (str, int, tuple, long)):
                show_tree.insert(tmp_id, END, text=str(const_item))
            elif type(const_item) == bytes:
                show_tree.insert(tmp_id, END, text=const_item)
            elif const_item == None:
                show_tree.insert(tmp_id, END, text='None')
            else:
                print("unhandle type", type(const_item))

        tmp_id = self.insert_params(parent, "co_names", "所有变量名")
        for name in pycode_object.co_names:
            show_tree.insert(tmp_id, END, text=name)

        tmp_id = self.insert_params(parent, "co_varnames", "约束变量 -本代码段中被赋值，但没有被内层代码段引用的变量")
        for name in pycode_object.co_varnames:
            show_tree.insert(tmp_id, END, text=name)

        tmp_id = self.insert_params(parent, "co_cellvars", "内层约束变量 -本代码段中被赋值，且被内层代码段引用的变量")
        for name in pycode_object.co_cellvars:
            show_tree.insert(tmp_id, END, text=name)

        tmp_id = self.insert_params(parent, "co_freevars", "自由变量- 本代码段中被引用，在外层代码段中被赋值的变量")
        for name in pycode_object.co_freevars:
            show_tree.insert(tmp_id, END, text=name)

        tmp_id = self.insert_params(parent, "co_code", "字节码指令", tab=3, open=not parent_id)
        if py_path:
            self.dis_code_with_source(pycode_object, show_tree, tmp_id, py_path)
        else:
            self.dis_code(pycode_object, show_tree, tmp_id)

        self.show_tree.insert(parent, END, text="")  # 留白
        
    

    def generate_pyc(self, py_path):
        pyc_name = None
 
        try:
            # 将源码编译成pycode对象
            with open(py_path) as source_fp:
                source = source_fp.read()
                code = compile(source, py_path, 'exec')
                
            # 将pycode对象保存为pyc格式
            pyc_name = os.path.splitext(py_path)[0] + '.pyc'
            with open(pyc_name, "wb") as code_fp:
                # 按照ceval.c 写入方式
                code_fp.write(imp.get_magic())
                py_compile.wr_long(code_fp, 0)
                marshal.dump(code, code_fp)
                code_fp.flush()
                code_fp.seek(4, 0)
                py_compile.wr_long(code_fp, int(time.time()))
                
        except IOError as error:
            showerror("生成PYC失败", "文件处理失败!{}".format(error))
        except Exception as error:
            showerror("生成PYC失败", "{}".format(error))
            
        return pyc_name

    def show_pyc(self, pyc_path, py_path=None):
        self.pycode_object = PycParser(pyc_path).insign()
        if self.parent:
            self.show_tree.delete(self.parent)
            self.parent = None
        self.run_button['state'] = 'normal'
        self.show_pyc_code(self.pycode_object, py_path=py_path)

    def open_py(self):
        py_path = filedialog.askopenfilename()
        if not py_path:
            return
        py_path = py_path.encode()
        pyc_path  = self.generate_pycpy_path       
        if pyc_path :
            self.show_pyc(pyc_path, py_path)

    def open_pyc(self):
        pyc_path = filedialog.askopenfilename()
        if not pyc_path:
            return
  
        pyc_path = pyc_path.encode()
        self.show_pyc(pyc_path)

    def outstream(self, message, newline=True):
        message = str(message)
        message += ('\n' if newline else ' ')
        self.out_stream.insert(END, message)
        self.out_stream.see(END)

    def run_code(self):

        if not hasattr(self, "out_vbar"):
            Label(text='运行输出').pack(fill=X)

            out_frame = Frame()
            self.out_vbar = Scrollbar(out_frame)
            self.out_vbar.pack(side=RIGHT, fill=Y)

            self.out_stream = Text(out_frame, background=self.background, font=self.font, foreground=self.main_color)
            self.out_stream.pack(side=LEFT,  fill=BOTH, expand=True)

            self.out_stream['yscrollcommand'] = self.out_vbar.set
            self.out_vbar['command'] = self.out_stream.yview

            out_frame.pack(fill=X)

        PythonVM(self.pycode_object, self.outstream).run_code()


def main():
    root = Tk()
    root.title("Pyc Insight")
    root.geometry('600x500')
    root.resizable(width=True, height=True)
    app = PycShowApplication(master=root)
    app.mainloop()


if __name__ == "__main__":
    main()
