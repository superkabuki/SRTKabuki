"""
srtkabuki.py

"""

import ctypes
import ctypes.util
import os
import sys
import time
import socket
import inspect


from static import SRT_DEFAULT_RECVFILE_BLOCK
from sockopts import SRTO_TRANSTYPE

# Socket Address structures


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


class sockaddr_in6(ctypes.Structure):  # For IPv6
    _fields_ = [
        ("sin6_family", ctypes.c_ushort),
        ("sin6_port", ctypes.c_ushort),
        ("sin6_flowinfo", ctypes.c_uint),
        ("sin6_addr", ctypes.c_ubyte * 16),
        ("sin6_scope_id", ctypes.c_uint),
    ]


class addrinfo(ctypes.Structure):
    pass  # Forward declaration for self-referential pointer


addrinfo._fields_ = [
    ("ai_flags", ctypes.c_int),
    ("ai_family", ctypes.c_int),
    ("ai_socktype", ctypes.c_int),
    ("ai_protocol", ctypes.c_int),
    ("ai_addrlen", ctypes.c_size_t),
    ("ai_addr", ctypes.POINTER(sockaddr)),
    ("ai_canonname", ctypes.c_char_p),
    ("ai_next", ctypes.POINTER(addrinfo)),
]


class sockaddr_storage(ctypes.Structure):
    _fields_ = [
        ("ss_family", ctypes.c_ushort),
        (
            "ss_data",
            ctypes.c_ubyte * (128 - ctypes.sizeof(ctypes.c_ushort)),
        ),  # Example size, adjust as needed
    ]


class SRTKabuki:
    """
    SRTKabuki Pythonic Secure Reliable Transport
    """

    def __init__(self, addr="0.0.0.0", port=9000):
        self.addr = addr
        self.port = port
        self.getaddrinfo, self.freeaddrinfo = self.load_libc()
        self.libsrt = self.load_srt()
        self.startup()
        self.sa_ptr, self.sa_size = self.mk_sockaddr_ptr(self.addr, self.port)
        self.sock = self.create_socket()
        self.peer_addr = None
        self.peer_addr_size = None
        self.peer_sock = None
        self.eid = None


    def load_libc(self):
        """
        load_libc load getaddrinfo and freeaddrinfo from libc.so
        """
        libc = ctypes.CDLL(ctypes.util.find_library("c"))
        getaddrinfo = libc.getaddrinfo
        getaddrinfo.argtypes = [
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(addrinfo),
            ctypes.POINTER(ctypes.POINTER(addrinfo)),
        ]
        getaddrinfo.restype = ctypes.c_int
        freeaddrinfo = libc.freeaddrinfo
        freeaddrinfo.argtypes = [ctypes.POINTER(addrinfo)]
        freeaddrinfo.restype = None
        return getaddrinfo, freeaddrinfo

    def load_srt(self):
        """
        load_srt load everything from libsrt.so
        """
        libsrt = None
        libsrt = ctypes.CDLL("libsrt.so")
        if not libsrt:
            raise OSError("failed to load libsrt.so")
        return libsrt

    def accept(self):
        """
        accept srt_accept
        """
        self.libsrt.srt_accept.restype = ctypes.c_int
        self.peer_addr = sockaddr_storage()
        self.peer_addr_size = ctypes.c_int(ctypes.sizeof(self.peer_addr))
        self.peer_sock = self.libsrt.srt_accept(
            self.sock, ctypes.byref(self.peer_addr), ctypes.byref(self.peer_addr_size)
        )
        self.getlasterror()
        return self.peer_sock

    def bind(self):
        """
        bind  srt_bind
        """
        self.libsrt.srt_bind.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
        self.libsrt.srt_bind.restype = ctypes.c_int
        self.libsrt.srt_bind(self.sock, self.sa_ptr, self.sa_size)
        self.getlasterror()

    def cleanup(self):
        """
        cleanup srt_cleanup
        """
        self.libsrt.srt_cleanup()
        self.getlasterror()

    def close(self, sock=None):
        """
        close srt_close
        """
        sock = self.chk_sock(sock)
        self.libsrt.srt_close.argtypes = [ctypes.c_int]
        self.libsrt.srt_close.restype = ctypes.c_int
        self.libsrt.srt_close(sock)
        self.getlasterror()

    def connect(self):
        """
        connect srt_connect
        """
        self.libsrt.srt_connect(self.sock, self.sa_ptr, self.sa_size)
        self.getlasterror()

    def create_socket(self):
        """
        create_socket srt_create_socket

        """
        self.libsrt.srt_create_socket.restype = ctypes.c_int
        ss = self.libsrt.srt_create_socket()
        self.getlasterror()
        return ss

    def epoll_create(self):
        """
        epoll_create srt_epoll_create
        """
        self.eid = self.libsrt.srt_epoll.create()
        self.getlasterror()

    def epoll_add_usock(self, events):
        """
        epoll_add_usock srt_epoll_add_usock
        """
        self.libsrt.srt_epoll_add_usock(self.eid, self.sock, ctypes.byref(events))
        self.getlasterror()

    def epoll_wait(self, readfds, writefds, ms_timeout, lrds, lwrds):
        """
        epoll_wait srt_epoll_wait
        """
        # srt_epoll_wait(epid, &srtrfds[0], &srtrfdslen, 0, 0, 100, 0, 0, 0, 0);
        # int srt_epoll_wait(int eid, SRTSOCKET* readfds, int* rnum, SRTSOCKET* writefds, int* wnum,
        # int64_t msTimeOut,
        #  SYSSOCKET* lrfds, int* lrnum, SYSSOCKET* lwfds, int* lwnum);
        self.libsrt.srt_epoll_wait(
            ctypes.byref(readfds),
            ctypes.byref(len(readfds)),
            ctypes.byref(writefds),
            ctypes.byref(len(writefds)),
            ctypes.c_int64(ms_timeout),
            ctypes.byref(lrfds),
            ctypes.byref(len(lrfds)),
            ctypes.byref(lwfds),
            ctypes.byref(len(lwfds)),
        )
        self.getlasterror()

    def getlasterror(self):
        """
        getlasterror srt_getlasterror_str

        """
        self.libsrt.srt_getlasterror_str.restype = ctypes.c_char_p
        caller = inspect.currentframe().f_back.f_code.co_name
        out= f"{caller}: {self.libsrt.srt_getlasterror_str().decode()}".replace("Success","✓")
        print(
            out, file=sys.stderr
        )

    def getsockstate(self, sock=None):
        """
        getsockstate srt_getsockstate
        """
        sock = self.chk_sock(sock)
        self.libsrt.srt_getsockstate(sock)
        self.getlasterror()

    def listen(self):
        """
        listen srt_listen
        """
        self.libsrt.srt_listen.argtypes = [ctypes.c_int, ctypes.c_int]
        self.libsrt.srt_listen(self.sock, 2)
        self.getlasterror()

    def recv(self, buffsize=1316, sock=None):
        """
        recv srt_recv
        """
        sock = self.chk_sock(sock)
        buffer = ctypes.create_string_buffer(buffsize)
        self.libsrt.srt_recv(sock, buffer, ctypes.sizeof(buffer))
        self.getlasterror()
        return buffer.raw

    def recvfile(self, local_filename, sock=None):
        """
        recvfile srt_recvfile
        """
        sock = self.chk_sock(sock)
        filesize = self.recv(sock=sock)
        offset = ctypes.c_int64(0)
        recvd_size = self.libsrt.srt_recvfile(
            sock,
            local_filename.encode("utf-8"),
            ctypes.byref(offset),
            filesize,
            SRT_DEFAULT_RECVFILE_BLOCK,
        )
        self.getlasterror()
        return recvd_size


    def recvmsg(self, buffsize=1316,sock=None):
        """
        recvmsg srt_recvmsg
        """
        sock = self.chk_sock(sock)
        buffer = ctypes.create_string_buffer(buffsize)
     #   self.libsrt.srt_recvmsg.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        st = self.libsrt.srt_recvmsg(
        sock, buffer, len(buffer)
        )
      #  self.getlasterror()
        return buffer.raw

    def send(self, msg, sock=None):
        """
        send srt_send
        """
        sock = self.chk_sock(sock)
        self.libsrt.srt_send(sock, msg, 64)
        self.getlasterror()

    def sendfile(self, filename, sock=None):
        """
        sendfile srt_sendfile
        """
        sock = self.chk_sock(sock)
        filesize = ctypes.c_int64(os.path.getsize(filename))
        offset = ctypes.c_int64(0)
        self.libsrt.srt_sendfile(
            sock,
            filename,
            ctypes.byref(offset),
            filesize,
            SRT_DEFAULT_RECVFILE_BLOCK,
        )
        self.getlasterror()


    def sendmsg2(self, msg, sock=None):
        """
        sendmsg2 srt_sendmsg2
        """
        sock = self.chk_sock(sock)
     #   msg = self.bytemsg(msg)
        st = self.libsrt.srt_sendmsg2(sock, msg, 32, None)
        self.getlasterror()
        time.sleep(0.001)

    def setsockflag(self, flag, val):
        """
        setsockflag  srt_setsockflag

        """
        val = ctypes.c_int(val)
        self.libsrt.srt_setsockflag(
            self.sock, flag, ctypes.byref(val), ctypes.sizeof(ctypes.c_int64))
        self.getlasterror()

    def startup(self):
        """
        startup  srt_startup()
        """
        self.libsrt.srt_startup()
        self.getlasterror()

    # helper methods not in libsrt

    def ipv4int(self, addr):
        """
        take a ipv4 string addr and make it an int
        """
        sa = int.from_bytes(socket.inet_pton(socket.AF_INET, addr), byteorder="little")
        self.getlasterror()
        return sa

    def mk_sockaddr_ptr(self, addr, port):
        """
        mk_sockaddr_sa make a c compatible (struct sockaddr*)&sa
        """
        sa_in = sockaddr_in()
        sa_in.sin_family = socket.AF_INET
        sa_in.sin_port = socket.htons(port)
        sa_in.sin_addr.s_addr = self.ipv4int(addr)
        # Get a pointer to sa_in
        sa_in_ptr = ctypes.pointer(sa_in)
        #  (struct sockaddr*)&sa
        return ctypes.cast(sa_in_ptr, ctypes.POINTER(sockaddr)), ctypes.sizeof(sa_in)

    def bytemsg(self, msg):
        """
        bytemsg convert python byte string
        to a C string buffer
        """
        if not isinstance(msg,(bytes,str)):
            msg = str(msg)
        if isinstance(msg,str):
            msg = msg.encode("utf8")
        if not isinstance(msg, bytes):
            msg = b"Message needs to be bytes"
        return ctypes.create_string_buffer(msg, len(msg))

    def request_file(self, remote_file):
        """
        request_file request a file from a server
        """
        remote_filename = remote_file.encode("utf8")
        msg = ctypes.create_string_buffer(remote_filename, len(remote_filename))
        rfl = str(len(remote_filename)).encode("utf8")  # remote file length
        rflen = ctypes.create_string_buffer(
            rfl, len(rfl)
        )  # remote file length written to a string buffer... I don't know.
        self.send(rflen)
        self.send(msg)
        self.getlasterror()

    def fetch(self, remote_file, local_file):
        """
        fetch fetch remote_file fron host on port
        and save it as local_file

        all args are strings.
        """
        yes = 1
        self.setsockflag(SRTO_TRANSTYPE, yes)
        self.connect()
        self.request_file(remote_file)
        self.recvfile(local_file)
        self.close()
        self.cleanup()

    def chk_sock(self,sock):
        """
        chk_sock if we don't have a sock, use self.sock
        """
        if not sock:
            sock=self.sock
        return sock
