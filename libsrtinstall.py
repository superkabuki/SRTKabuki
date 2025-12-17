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
    return Popen(cmd, stderr=PIPE, stdout=PIPE).communicate()


def do(cmd):
    """
    do run command and print output
    """
    out, errs = runcmd(cmd)
    print("OUT")
    splitprint(out)
    print("ERRS")
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
            print(f"{prog} found")
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
    print(os.getcwd())
    
    do(["cmake", "build", ".", "--install-prefix",f'{os.getcwd()}/../srtfu'])
    make = pickmake()
    do([make, "install"])


#libsrtinstall()
# path=f'{os.path.dirname(__file__)}/libsrt.so'
