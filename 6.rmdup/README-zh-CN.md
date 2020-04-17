# rmdup-移除重复文件
=========================

这个脚本可以用来删除当前文件夹下的重复文件，rmdup 即 remove duplicated 的缩写。

执行样例

```
>./rmdup.py
Scanning files in [current directory]
74060 files scanned, 11413 duplicated files found.
delete?(y/n/f) > 
```

y: 直接删除所有检测到的文件（慎用）

n: 退了退了

f: 把检测到的文件写入 rmdup.files 文件里，供你检查，检查完以后按F键删除。rmdup.files的文件格式是```检测到与某文件重复的文件>>>之前检测到的某文件```，删除时会删除>>>前面的所有文件。

```
[rmdup.files]
fileA>>>fileB
fileC>>>fileB
fileD>>>fileB
```

那么 fileA/C/D 会被删除。

## 自写自用，风险自负