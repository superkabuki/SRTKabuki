"""
This is SRTfu version of examples/test-c-server.c in libsrt.
https://github.com/Haivision/srt/blob/master/examples/test-c-server.c
"""

import ctypes
import sys
from srtfu import SRTfu
from srtfu  import SRTO_RCVSYN


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <srt_url>", file=sys.stderr)
        sys.exit(1)
    srt_url = sys.argv[1]
    srtf = SRTfu(srt_url)  # srt://example.com:9000
    srtf.create_socket()
    yes = 1
    srtf.setsockflag(SRTO_RCVSYN, yes)
    srtf.bind()
    print(srtf.getsockstate())
    srtf.listen()
    fhandle = srtf.accept()
    print("Accepted connection. Waiting for messages...")
    msg_buffer = srtf.mkbuff(1316)
    while True:
        st = srtf.recvmsg(msg_buffer, fhandle)
        if st == -1:
            print("minus one")
            break
        else:
            print(f"Got msg of len {st} << {msg_buffer.raw.decode(errors='ignore')}")


if __name__ == "__main__":
    main()
