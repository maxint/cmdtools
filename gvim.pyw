#!/usr/bin/env python
# encoding: utf-8

import subprocess
import os
import sys
import string

p = subprocess.Popen('vim --serverlist', shell=True, creationflags=subprocess.SW_HIDE, stdout=subprocess.PIPE)
out, err = p.communicate()
sname = out.strip()
print sname
argvs = string.join(sys.argv[1:], ' ')
if sname:
   cmd = 'gvim --servername {} --remote {}'.format(sname, argvs)
else:
   cmd = 'gvim --servername GVIM {}'.format(argvs)
print cmd
subprocess.Popen(cmd, creationflags=subprocess.SW_HIDE)
