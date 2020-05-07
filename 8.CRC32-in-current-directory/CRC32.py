# /bin/env python

import os
import sys
import zlib
import locale


def crc(fileName):
    prev = 0
    for eachLine in open(fileName, "rb"):
        prev = zlib.crc32(eachLine, prev)
    return "%8X" % (prev & 0xFFFFFFFF)


current_encoding = locale.getpreferredencoding()

with open("crc32.txt", "w+", encoding=current_encoding) as output:
    op = ["[-CRC-32-] FileName\n", "--------------\n"]
    for i in os.listdir():
        if os.path.isfile(i) and not "crc" in i.lower():
            print(f"[{crc(i)}]{i}")
            op.append(f"[{crc(i)}]{i}\n")
    output.writelines(op)
