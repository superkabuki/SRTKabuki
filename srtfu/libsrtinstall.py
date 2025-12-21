'''
libsrtinstall.py
'''


import os
import sys
from subprocess import Popen, PIPE


WHITEY='\033[0;97m'

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
            print(line.decode(),file=sys.stderr)


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
    out, _ = runcmd(["uname"])
    if out.strip() == b"OpenBSD":
        make = "gmake"
    print(f"{WHITEY}srtfu - Using {make} for make",file=sys.stderr)
    return make


def check_program(prog):
    """
    check_program check if a
    program is installed
    """
    out, _ = runcmd(["which", prog])
    if out:
        print(f"{WHITEY}srtfu - {prog}\t\tfound",file=sys.stderr)
    else:
        print(f"{WHITEY}srtfu - {prog} is required for libsrt",file=sys.stderr)
        sys.exit()


def check_depends():
    """
    check_depends check for deps
    needed to build libsrt
    """
    depends = ["git", "openssl", "cmake"]
    while depends:
        program = depends.pop()
        check_program(program)


def makes():
    """
    makes run cmake,
    and make.
    """
    print(f"{WHITEY}srtfu - Running cmake",file=sys.stderr)
    do(["cmake", "build", "."])   
    make = pickmake()
    print(f"{WHITEY}srtfu - Running {make}",file=sys.stderr)
    do([make, "all"])


def copy_so_files():
    """
    copy_so_files copy lib srt .so fiiles
    to site_packages/srtfu
    """
    install_path=os.path.dirname(__file__)
    print(f"{WHITEY}srtfu - Install path is {install_path}",file=sys.stderr)
    _=[do(['cp',so,install_path]) for so in os.listdir('.') if so.startswith('libsrt.so')]


def cleanup():
    """
    cleanup delete srt build dir
    """
    os.chdir('../')
    print(f"{WHITEY}srtfu - Removing srt build dir",file=sys.stderr)
    do(['rm','-rf','srt'])    


def libsrtinstall():
    """
    libsrtinstall install libsrt
    """
    print(f'{WHITEY}\nsrtfu - Building shared lib for libsrt\n', file=sys.stderr)

    check_depends()
    do(["git", "clone", "https://github.com/Haivision/srt"])
    os.chdir("srt")
    makes()
    copy_so_files()
    cleanup()
