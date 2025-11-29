"""
This is SRTKabuki version of examples/test-c-server.c in libsrt.
https://github.com/Haivision/srt/blob/master/examples/test-c-server.c
"""

import ctypes
import sys
from srtkabuki import SRTKabuki
from srtkabuki.srt_h import SRTO_RCVSYN


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <srt_url>", file=sys.stderr)
        sys.exit(1)
    srt_url = sys.argv[1]
    srtk = SRTKabuki(srt_url)  # srt://example.com:9000
    srtk.create_socket()
    yes = 1
    srtk.setsockflag(SRTO_RCVSYN, yes)
    srtk.bind()
    print(srtk.getsockstate())
    srtk.listen()
    fhandle = srtk.accept()
    print("Accepted connection. Waiting for messages...")
    msg_buffer = srtk.mkbuff(1316)
    while True:
        st = srtk.recvmsg(msg_buffer, fhandle)
        if st == -1:
            print("minus one")
            break
        else:
            print(f"Got msg of len {st} << {msg_buffer.raw.decode(errors='ignore')}")


if __name__ == "__main__":
    main()
