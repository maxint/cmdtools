# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

import subprocess
import sys

if subprocess.check_output('vim --serverlist',
                           shell=True,
                           creationflags=subprocess.SW_HIDE).strip():
    cmd = 'gvim --remote-silent '
else:
    cmd = 'gvim --servername GVIM '

subprocess.Popen(cmd + ' '.join(sys.argv[1:]),
                 creationflags=subprocess.SW_HIDE)
