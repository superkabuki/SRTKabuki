'''
This is SRTKabuki version of examples/test-c-client.c in libsrt.
https://github.com/Haivision/srt/blob/master/examples/test-c-client.c
'''

import sys
import time
from srtkabuki import SRTKabuki
from sockopts import SRTO_SENDER


def main():
    srt_url = sys.argv[1] # srt://example.com:9000
    srtk = SRTKabuki(srt_url)
    srtk.setsockflag(SRTO_SENDER, 1)
    srtk.connect()
    a = 100
    while a:
        a -= 1
        srtk.sendmsg2(b"I am super cool")
        time.sleep(0.01)
    time.sleep(1)
    srtk.close()
    srtk.cleanup()


main()
