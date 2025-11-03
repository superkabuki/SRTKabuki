'''
This is a rewrite of the test-c-server.c in the libsrt examples in python.
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
    srtk = SRTKabuki()
    srtk.host = sys.argv[1]
    srtk.port = int(sys.argv[2])
    srtk.create_socket()
    yes = ctypes.c_int(1)
    srtk.setsockflag(SRTO_RCVSYN, yes)
    srtk.bind()
    srtk.listen()
    srtk.accept()
    print("Accepted connection. Waiting for messages...")
    st = 50
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
