跟踪结果比对工具


# 安装

- Python 2.7 (\\maxint-w7\DEVELOP\python\python-2.7.3.msi)


# 程序

## `ot_report.bat`

本脚本从手机pull跟踪数据到当前工作目录的`data`子目录下，再对比`*_fingerMarks.txt`和
`*_fingerMarks_res.txt`的结果到`*_fingerMarks_res.csv`。

## `rect_compare.bat`

通用矩形框比较工具，自动比较指定目录下的所有`<name>_fingerMark.txt`和`<name>_*.txt`文件对。


# 帮助

```
ot_report.bat -h
rect_compare.bat -h
```
