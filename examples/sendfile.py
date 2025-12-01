import ctypes
import sys
import os
import time
import socket
from ctypes.util import find_library
from srtfu import SRTfu
from srtfu import SRTO_TRANSTYPE
from srtfu import SRT_FILE


def send_a_file(srtf):
    """
    send_a_file accept a connection,
    read filename size from socket,
    read filename from socket,
    sendfile to client
    close connection
    """
    fhandle = srtf.accept()
    srtf.getsockstate()
    srtf.getsockstate(fhandle)
    print(f"Accepted new connection (socket ID: {fhandle})...")
    smallbuff = srtf.mkbuff(1316)
    srtf.recvmsg(smallbuff, fhandle)
    filenamesize = int.from_bytes(smallbuff.value, byteorder="little")
    print("filenamesize ", filenamesize)
    fbuff = srtf.mkbuff(filenamesize)
    srtf.recv(fbuff, fhandle)
    try:
        srtf.sendfile(fbuff.value, fhandle)
    except:
        print(f"File {fbuff.value.decode()} Not Found.")
    finally:
        time.sleep(1)
        srtf.close(fhandle)
        srtf.getlasterror()


def go():
    """
    go create an SRTfu instance,
    set the sock flag for files,
    bind it to 0.0.0.0 port 9000,
    accept connections
    """
    srtf = SRTfu("srt://0.0.0.0:9000")
    srtf.setsockflag(SRTO_TRANSTYPE, SRT_FILE)
    srtf.bind()
    srtf.listen()
    print("Waiting for connections...")
    while True:
        send_a_file(srtf)


if __name__ == "__main__":
    go()
