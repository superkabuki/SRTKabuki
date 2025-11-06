import ctypes
import sys
import os
import time
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
# Accept multiple client connections (infinite loop simulation)
print("Waiting for connections...")

while True:
    fhandle = srtk.accept() 
    print(f"Accepted new connection (socket ID: {fhandle})...")
    buffer_size = 8
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
    time.sleep(1)
    srtk.close(fhandle)
    srtk.getlasterror()


if __name__ == "__main__":
    main()
