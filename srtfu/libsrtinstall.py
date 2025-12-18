'''
libsrtinstall.py
'''


import os
import sys
from subprocess import Popen, PIPE


def splitprint(data):
    """
    splitprint split data
    into lines and print
    """
    if isinstance(data, int):
        print(data)
    else:
        lines = data.split(b"\n")
        for line in lines:
            print(line.decode())


def runcmd(cmd):
    """
    runcmd Popen a command
    """
    return Popen(cmd,stderr=PIPE, stdout=PIPE).communicate()


def do(cmd):
    """
    do run command and print output
    """
    out, errs = runcmd(cmd)
    splitprint(out)
    splitprint(errs)


def pickmake():
    """
    pickmake use make or gmake
    """
    make = "make"
    out, errs = runcmd(["uname"])
    if out.strip() == b"OpenBSD":
        make = "gmake"
    print(f"using {make} for make")
    return make


def runchks():
    """
    runchks check for deps
    needed to build libsrt
    """
    chks = ["git", "openssl", "cmake"]
    while chks:
        prog = chks.pop()
        out, errs = runcmd(["which", prog])
        if out:
            print(f"{prog}\tfound")
        else:
            print(f"{prog} is required for libsrt")
            sys.exit()


def libsrtinstall():
    """
    libsrtinstall install libsrt
    """
    runchks()
    do(["git", "clone", "https://github.com/Haivision/srt"])
    os.chdir("srt")
    do(["cmake", "build", "."])
    make = pickmake()
    do([make, "all"])
    _=[do(['cp',so,f'{os.path.dirname(__file__)}']) for so in os.listdir('.') if so.startswith('libsrt.so')]
    os.chdir('../')
    do(['rm','-rf','srt'])
