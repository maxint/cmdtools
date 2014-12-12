#!/bin/usr/env python
import getopt, sys
import hashlib

if __name__=='__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'k:')
    except getopt.GetoptError:
        # print help information and exit
        usage()
        sys.exit(2)

    keypass = None
    for o, a in opts:
        if o == "-k":
            keypass = a

    keypass = args[0]
    m = hashlib.md5(keypass)
    print(m.hexdigest()[:14])
