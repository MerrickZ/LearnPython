#/bin/env python

import zlib
import os,sys

def crc(fileName):
	prev = 0
	for eachLine in open(fileName,"rb"):
		prev = zlib.crc32(eachLine, prev)
	return "%8X"%(prev & 0xFFFFFFFF)

with open("crc32.txt","w+",encoding="GBK") as output:
	op=["[-CRC-32-]FILE\n","--------------\n"]
	for i in os.listdir():
		if os.path.isfile(i) and not "crc" in i.lower() :
			print(f"[{crc(i)}]{i}")
			op.append(f"[{crc(i)}]{i}\n")
	output.writelines(op)