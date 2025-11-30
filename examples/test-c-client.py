"""
This is SRTfu version of examples/test-c-client.c in libsrt.
https://github.com/Haivision/srt/blob/master/examples/test-c-client.c
"""

import sys
import time
from srtfu import SRTfu
from srtfu import SRTO_SENDER


def main():
    srt_url = sys.argv[1]  # srt://example.com:9000
    srtf = SRTfu(srt_url)
    srtf.setsockflag(SRTO_SENDER, 1)
    srtf.connect()
    a = 100
    while a:
        a -= 1
        srtf.sendmsg2(b"I am super cool")
        time.sleep(0.01)
    time.sleep(1)
    srtf.close()
    srtf.cleanup()


main()
