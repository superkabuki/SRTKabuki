import ctypes
import sys
import os
import time
import socket
from ctypes.util import find_library
from srtkabuki import SRTKabuki
from srtkabuki.srt_h import SRTO_TRANSTYPE
from srtkabuki.srt_h import SRT_FILE


def send_a_file(srtk):
    """
    send_a_file accept a connection,
    read filename size from socket,
    read filename from socket,
    sendfile to client
    close connection
    """
    fhandle = srtk.accept()
    srtk.getsockstate()
    srtk.getsockstate(fhandle)
    print(f"Accepted new connection (socket ID: {fhandle})...")
    smallbuff = srtk.mkbuff(1316)
    srtk.recv(smallbuff, fhandle)
    filenamesize = int.from_bytes(smallbuff.value, byteorder="little")
    print("filenamesize ", filenamesize)
    fbuff = srtk.mkbuff(filenamesize)
    srtk.recv(fbuff, fhandle)
    try:
        srtk.sendfile(fbuff.value, fhandle)
    except:
        print(f"File {fbuff.value.decode()} Not Found.")
    finally:
        time.sleep(1)
        srtk.close(fhandle)
        srtk.getlasterror()


def go():
    """
    go create an SRTKabuki instance,
    set the sock flag for files,
    bind it to 0.0.0.0 port 9000,
    accept connections
    """
    srtk = SRTKabuki("srt://0.0.0.0:9000")
    srtk.setsockflag(SRTO_TRANSTYPE, SRT_FILE)
    srtk.bind()
    srtk.listen()
    print("Waiting for connections...")
    while True:
        send_a_file(srtk)


if __name__ == "__main__":
    go()
