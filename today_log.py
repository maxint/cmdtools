# coding: utf-8
# author: maxint <NOT_SPAM_lnychina@gmail.com>

"""

"""

import subprocess
import time
from Tkinter import Tk

log = subprocess.check_output('git log --since="1 day ago" --format="- %s"')
log = log.strip()
print '=' * 20
print log
print '=' * 20

# copy to system clipboard
r = Tk()
r.withdraw()
r.clipboard_clear()
r.clipboard_append(log)
r.destroy()

print 'Done!'
time.sleep(1)
