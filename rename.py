#!/usr/bin/env python3

import os
import sys

print(f"renaming {sys.argv[1]}")

def renameDir(directory):
    for f in os.listdir(directory):
        src = os.path.join(directory,f)
        dst = os.path.join(directory,f.lower())
        print(f"{src} -> {dst}")
        os.rename(src, dst)

for root, dirs, files in os.walk(sys.argv[1], topdown=False):
    for name in dirs:
        src = os.path.join(root,name)
        dst = os.path.join(root,name.lower())
        renameDir(src)
        print(f"{src} -> {dst}")
        os.rename(src,dst)
renameDir(sys.argv[1])
