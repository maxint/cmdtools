#! /usr/bin/env python
#  coding: utf-8

import os
import subprocess
import re

def run(cmd):
    subprocess.check_call(cmd)

def runout(cmd):
    return subprocess.check_output(cmd)

if __name__ == '__main__':
    assert os.name == 'nt', 'This script could only run in Windows'

    import argparse

    class readable(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            path = values
            if os.path.splitext(path)[1].lower() != '.dll':
                msg = '{0} is not a dll file'.format(path)
                parser.error(msg)
            if not os.path.isfile(path):
                msg = '{0} is not a valid path'.format(path)
                parser.error(msg)
            if not os.access(path, os.R_OK):
                msg = '{0} is not a readable path'.format(path)
                parser.error(msg)
            setattr(namespace, self.dest, path)

    parser = argparse.ArgumentParser(description='Generate lib from dll')
    parser.add_argument('dll', action=readable, help='dll file path')

    args = parser.parse_args()

    name = os.path.splitext(os.path.basename(args.dll))[0]
    def_path = name + '.def'
    lib_path = name + '.lib'

    print '[I] Generating ' + def_path
    cmd = 'dumpbin /exports ' + args.dll
    out = runout(cmd)

    func_names = re.findall(r'\s+\d{1,2}\s+\d{1,2} [\dA-Z]{8} (\w+)', out)
    with open(def_path, 'wt') as f:
        f.write('\n'.join(['EXPORTS'] + func_names))

    print '[I] Generating ' + lib_path
    cmd = 'lib /def:{} /out:{}.lib'.format(def_path, lib_path)
    runout(cmd)

    print 'Done!'