# REMOVE DUPLICATED FILES
=========================

This script is used to remove all duplicated files in current working directory.


```
>./rmdup.py
Scanning files in [current directory]
74060 files scanned, 11413 duplicated files found.
delete?(y/n/f) > 
```

y: delete all duplicated files.

n: quit.

f: load from generated rmdup.files file, you may edit it or check which files were to be deleted.

```
[rmdup.files]
fileA>>>fileB
fileC>>>fileB
fileD>>>fileB
```

Then fileA/C/D will be deleted.