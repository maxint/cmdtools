import hashlib
import sys
import win32clipboard as wincb
import win32con
import os

if __name__=='__main__':
    key = sys.argv[1]
    md5pass = hashlib.md5(key).hexdigest()[:14]
    wincb.OpenClipboard()
    wincb.EmptyClipboard()
    wincb.SetClipboardData(win32con.CF_TEXT, md5pass)
    print("Clipboard Data: "+wincb.GetClipboardData(win32con.CF_TEXT))
    wincb.CloseClipboard()
    #raw_input("Press any key to exit!")
    os.system("pause")
