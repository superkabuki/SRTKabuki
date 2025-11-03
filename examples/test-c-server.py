'''
This is SRTKabuki version of examples/test-c-server.c in libsrt.
https://github.com/Haivision/srt/blob/master/examples/test-c-server.c
'''

import ctypes
import sys
from srtkabuki import SRTKabuki
from static import SRTO_RCVSYN


def main():
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <host> <port>", file=sys.stderr)
        sys.exit(1)
    srtk = SRTKabuki(addr=sys.argv[1], port=int(sys.argv[2]))
    srtk.create_socket()
    yes = 1
    srtk.setsockflag(SRTO_RCVSYN, yes)
    srtk.bind()
    srtk.listen()
    srtk.accept()
    print("Accepted connection. Waiting for messages...")
    msg_buffer = ctypes.create_string_buffer(1316)
    while True:
        st = srtk.recvmsg(msg_buffer)
        if st == -1:
            print("minus one")
            break
        else:
            print(f"Got msg of len {st} << {msg_buffer.value.decode(errors='ignore')}")


if __name__ == "__main__":
    main()
