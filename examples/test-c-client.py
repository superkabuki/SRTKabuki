'''
This is SRTKabuki version of examples/test-c-client.c in libsrt.
https://github.com/Haivision/srt/blob/master/examples/test-c-client.c
'''

import sys
import ctypes
from srtkabuki import SRTKabuki
from static import SRTO_SENDER


def main():
    srtk = SRTKabuki(addr=sys.argv[1], port=int(sys.argv[2]))
    srtk.setsockflag(SRTO_SENDER, 1)
    srtk.connect()
    a = 9
    while a:
        a -= 1
        srtk.sendmsg2(b"I am super cool")

    srtk.close()
    srtk.cleanup()


main()
