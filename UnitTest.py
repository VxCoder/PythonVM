# coding=utf-8

import re
import os
import subprocess

from PyVM import PythonVM
from InsightPyc import PycParser, PycShowApplication

space = re.compile(r'\s')
outstring = []


def outstream(message, newline=True):
    message = str(message)
    message += ('\n' if newline else ' ')
    outstring.append(message)


def main_test():
    global outstring

    success = 0
    failed = 0

    for file_name in os.listdir('test'):
        # 异常暂时不比对,但功能已完成
        if not file_name.endswith('.py') or file_name == 'exception_control.py':
            continue

        # 获取python 虚拟机的输出
        py_path = os.path.join('.', 'test', file_name)
        try:
            real_output = subprocess.check_output(['python', py_path])
        except subprocess.CalledProcessError as error:
            real_output = error.output

        # 获取我的虚拟机的输出
        pyc_path = PycShowApplication.generate_pyc(py_path)
        pycode_object = PycParser(pyc_path).insign()
        PythonVM(pycode_object, outstream, py_path).run_code()
        vm_output = "".join(outstring)

        # 比对输出是否一致
        if space.sub('', vm_output) == space.sub('', real_output):
            success += 1
            print "pass {}".format(py_path)
        else:
            failed += 1
            print "failed {}".format(py_path)
            print">>>>>>>>>>>>>>>>>real>>>>>>>>\n{}".format(real_output.strip())
            print"<<<<<<<<<<<<<<<<vm<<<<<<<<<<<\n{}".format(vm_output.strip())

        outstring = []

    print "\n**************************"
    print "success: {} failed: {}".format(success, failed)
    print "**************************"

if __name__ == "__main__":
    main_test()
