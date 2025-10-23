

import ctypes
import sys
import socket
import time

YES = 1
SRTO_SENDER = 21
PORT = 9000
ADDR = "127.0.0.1"



class sockaddr(ctypes.Structure):
    _fields_ = [
        ("sa_family", ctypes.c_ushort),
        ("sa_data", ctypes.c_char * 14),  # 14 bytes for address data
    ]


class in_addr(ctypes.Structure):
    _fields_ = [("s_addr", ctypes.c_uint32)]  # IPv4


class sockaddr_in(ctypes.Structure):
    _fields_ = [
        ("sin_family", ctypes.c_short),
        ("sin_port", ctypes.c_ushort),
        ("sin_addr", in_addr),
        ("sin_zero", ctypes.c_char * 8),
    ]


class SRTKabuki:

    def __init__(self,addr,port):
        self.addr=addr
        self.port=port
        self.mesg=None
        self.file=None
        self.libsrt = ctypes.CDLL("libsrt.so")
        self.libsrt.srt_getlasterror_str.restype = ctypes.c_char_p
        self.libsrt.srt_startup()
        self.sa_ptr, self.sa_size = self.mk_sockaddr_ptr(self.addr, self.port)
        print(f"SRTKabuki.mk_sockaddr_ptr: {self.libsrt.srt_getlasterror_str()}")
        self.sock = self.libsrt.srt_create_socket()
        print(f"LibSRT srt_create_socket: {self.libsrt.srt_getlasterror_str()}")

    def set_sock_flag(self,flag):
        self.libsrt.srt_setsockflag(self.sock, flag, 1, 32)
        print(f"SRTKabuki set_sock_flag: {self.libsrt.srt_getlasterror_str()}")

    def connect(self):
        """
        connect  is srt_connect()
        """
        self.libsrt.srt_connect(self.sock, self.sa_ptr, 64)        
        print(f"LibSRT srt_connect: {self.libsrt.srt_getlasterror_str()}")


    def done(self):
        """
        done close the socket and call cleanup.
        """
        self.libsrt.srt_close(self.sock)
        print(f"LibSRT srt_close: {self.libsrt.srt_getlasterror_str()}")
        self.libsrt.srt_cleanup()
        print(f"SRTKabuki.done: {self.libsrt.srt_getlasterror_str()}")

    def write_mesg(self,mesg):
        """
        write message format byte string for C
        and write it to the socket
        """
        mesg = self.byte_mesg(mesg)
        st = self.libsrt.srt_sendmsg2(self.sock, mesg, ctypes.sizeof(mesg), None)
        if st:
            print(f"SRTKabuki.write_mesg: {self.libsrt.srt_getlasterror_str()}")
        time.sleep(0.1)
        

    def  byte_mesg(self,mesg):
        """
        byte_mesg convert python byte string
        to a C string buffer
        """
        if not isinstance(mesg,bytes):
            mesg =b"Message needs to be bytes"
        return ctypes.create_string_buffer(mesg, 15)

    def ipv4int(self,addr):
        """
        take a ipv4 string addr and make it an int
        """
        sa = int.from_bytes(socket.inet_pton(socket.AF_INET, addr), byteorder="little")
        print(f"SA {sa}")
        return sa

    def mk_sockaddr_ptr(self,addr, port):
        """
        mk_sockaddr_sa make a c compatible (struct sockaddr*)&sa
        """
        sa_in = sockaddr_in()
        sa_in.sin_family = socket.AF_INET
        sa_in.sin_port = socket.htons(self.port)
        sa_in.sin_addr.s_addr = self.ipv4int(self.addr)
        # socket.inet_pton(socket.AF_INET, addr)
        # Get a pointer to sa_in
        sa_in_ptr = ctypes.pointer(sa_in)
        #  (struct sockaddr*)&sa
        return ctypes.cast(sa_in_ptr, ctypes.POINTER(sockaddr)), ctypes.sizeof(sa_in)


if __name__ =='__main__':
    srtk=SRTKabuki('127.0.0.1',9000)
    srtk.set_sock_flag(SRTO_SENDER)
    srtk.connect()
    a = 9
    while a:
        a -=1
        srtk.write_mesg(b'I am super cool')
       # time.sleep(0.1)
    srtk.done()
    
