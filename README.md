
![](https://img.shields.io/badge/python-2.7-brightgreen.svg)
![](https://travis-ci.org/VxCoder/PythonVM.svg?branch=master)
# PythonVM
通过python实现python虚拟机

# 暂时实现的功能
主要功能脚本：InsightPyc.py

## PYC文件解析
  1. 打开pyc文件并显示解析结果
  2. 打开py文件,生成pyc文件并解析显示
  3. 显示python汇编代码(py方式打开,可以有源码对照)

## 模拟运行
  1. 模拟运行功能, 现支持的汇编指令(参见OpCode.py 有#标志的指令)


## 源码文件编辑
  1. 有个运行界面了

     
# 有空要开发的功能
1. 完善pyc中剩余类型的解析
2. 参考byterun项目/ceval.c 实行python执行引擎（这么大的功能，就这么一笔带过了)
3. 完善GUI显示
4. 支持python3.x
5. 从汇编代码中逆推出源代码
6. co_consts 附带类型

