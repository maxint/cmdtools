# 简介

本脚本从手机pull跟踪数据到当前工作目录的data子目录下，再对比`*_fingerMarks.txt`和
`*_fingerMarks_res.txt`的结果到`*_fingerMarks_res.csv`。

# 安装

- Python2.7 (\\maxint-w7\DEVELOP\python\python-2.7.3.msi)

# 程序

- `ot_report.bat`： OT 结果比较程序，支持从手机指定目录下载跟踪结果文件。
- `rect_compare.bat`：通用矩形框比较工具，自动比较指定目录下的所有`<name>_fingerMark.txt`和`<name>_*.txt`文件对。

# 帮助

```
ot_report.bat -h
rect_compare.bat -h
```
