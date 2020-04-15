#!/usr/bin/python3

# Merrick Zhang<anphorea@gmail.com>
# Licensed under MIT.

# Find duplicated files
# Step 1: get all file sizes
# Step 2: get MD5 for same size files, if fits, append to to-delete-list.
# Step 3: remove duplicated files

import hashlib
import os
from functools import partial
from os.path import getsize, join

#################
# Get File Hash #
#################


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        for buf in iter(partial(f.read, 128), b''):
            d.update(buf)
    return d.hexdigest()

####################
# File Node Struct #
####################


class node():
    filepath = None
    filesize = None
    filehash = None

    def __init__(self, fpath):
        self.filepath = fpath
        self.filesize = getsize(fpath)

    def gethash(self):
        if not self.filehash:
            self.filehash = md5sum(self.filepath)
        return self.filehash

    def __hash__(self):
        return self.filesize


# starts from current directory
current_directory = os.getcwd()
print("Finding duplicate files in ", current_directory)

huge_hash_table = {}
to_delete_list = []

for root, dirs, files in os.walk(current_directory):
    for file in files:
        p = node(os.path.join(root, file))
        fz = str(p.filesize)
        if fz in huge_hash_table.keys():
            # compare md5 hash
            hash_of_p = p.gethash()
            dup_flag = False

            for i in huge_hash_table[fz]:
                if not dup_flag and (hash_of_p == i.gethash()):
                    dup_flag = True

            if dup_flag:
                # mark for delete
                to_delete_list.append(p)
        else:
            if fz in huge_hash_table.keys():
                huge_hash_table[fz].append(p)
            else:
                huge_hash_table[fz] = []
                huge_hash_table[fz].append(p)

print("Files to be deleted:")
log = open("rmdup.files", "w+")
for i in to_delete_list:
    print(i.filepath)
    print(i.filepath, file=log)
log.close()

print("Checkout rmdup.files for details.")

s = input("Just delete ALL(y/n/f)? F to load entries from rmdup.files >")
if (s.lower == "y"):
    for i in to_delete_list:
        print("Deleting ", i.filepath)
        os.remove(i.filepath)

if (s.lower == "f"):
    with open("rmdup.files", "r") as f:
        for line in f.readlines():
            print("Deleting ", line)
            os.remove(line)
