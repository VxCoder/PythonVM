# PythonVM
通过python实现python虚拟机

# 暂时实现的功能
主要功能脚本：InsightPyc.py

## PYC文件的解析
  1. 查找pyc文件并显示解析结果
  2. 打开当前目录的py文件,生成pyc文件并解析显示
  3. 显示python汇编代码(py方式打开,可以有源码对照)

## PYC文件运行
  1. 模拟运行功能, 现支持的汇编指令如下(共119条指令):
      * 2 ROT_TWO
      * 3 ROT_THREE
      * 4 DUP_TOP
      * 5 ROT_FOUR
      * 54 STORE_MAP
      * 60 STORE_SUBSCR
      * 71 PRINT_ITEM   
      * 72 PRINT_NEWLINE
      * 83 RETURN_VALUE
      * 90 HAVE_ARGUMENT
      * 90 STORE_NAME 
      * 100 LOAD_CONST
      * 101 LOAD_NAME
      * 102 BUILD_TUPLE
      * 103 BUILD_LIST
      * 105 BUILD_MAP
     
# 有空要开发的功能
1. 完善pyc中剩余类型的解析
2. 任意路径下py文件的解析
3. 参考byterun项目/ceval.c 实行python执行引擎（这么大的功能，就这么一笔带过了)
4. 完善GUI显示
5. 支持python3.x
6. 反汇编功能
7. co_consts 附带类型