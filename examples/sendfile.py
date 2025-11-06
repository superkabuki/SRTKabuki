import ctypes
import sys
import os
import socket
from ctypes.util import find_library
from srtkabuki import SRTKabuki
from sockopts import SRTO_TRANSTYPE

SRT_ERROR = -1
SRT_INVALID_SOCK = -1

srtk = SRTKabuki("0.0.0.0", 9000)
yes = 1
srtk.setsockflag(SRTO_TRANSTYPE, yes)
srtk.bind()
srtk.listen()
print("Waiting for connections...")
while True:
    fhandle = srtk.accept()  # serv, client_sa_ptr, ctypes.pointer(addrlen_int))
    if fhandle == SRT_INVALID_SOCK:
        print(f"Accept error: {srt.srt_getlasterror_str().decode('utf-8')}")
        break
    print(f"Accepted new connection (socket ID: {fhandle})...")
    buffer_size = 1024
    # buffer = ctypes.create_string_buffer(buffer_size)
    data = srtk.recv(
        buffer_size,
        fhandle,
    )
    print(data)
    filenamesize = int(data)
    print(filenamesize)
    filename = srtk.recv(
        filenamesize,
        fhandle,
    )
    print(filename)
    srtk.getlasterror()
    srtk.sendfile(filename, fhandle)
    srtk.close(fhandle)
    srtk.getlasterror()


if __name__ == "__main__":
    main()
