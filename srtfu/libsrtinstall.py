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
    print(f"using {make} for make",file=sys.stderr)
    return make


def check_program(prog):
    """
    check_program check if a
    program is installed
    """
    out, _ = runcmd(["which", prog])
    if out:
        print(f"{prog}\tfound",file=sys.stderr)
    else:
        print(f"{prog} is required for libsrt",file=sys.stderr)
        sys.exit()


def runchks():
    """
    runchks check for deps
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
    do(["cmake", "build", "."])
    make = pickmake()
    do([make, "all"])


def copy_so_files():
    """
    copy_so_files copy lib srt .so fiiles
    to site_packages/srtfu
    """
    install_path=os.path.dirname(__file__)
    _=[do(['cp',so,install_path]) for so in os.listdir('.') if so.startswith('libsrt.so')]


def cleanup():
    """
    cleanup delete srt build dir
    """
    os.chdir('../')
    do(['rm','-rf','srt'])    


def libsrtinstall():
    """
    libsrtinstall install libsrt
    """
    runchks()
    do(["git", "clone", "https://github.com/Haivision/srt"])
    os.chdir("srt")
    makes()
    copy_so_files()
    cleanup()
