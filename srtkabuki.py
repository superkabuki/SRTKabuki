"""
srtkabuki.py

"""

import ctypes
import ctypes.util
import sys
import os
import socket
import struct
import inspect


from static import (
    SRT_DEFAULT_RECVFILE_BLOCK,
    SRTO_TRANSTYPE,
    SOCK_DGRAM,
    AF_INET,
    AI_PASSIVE,
    SRT_ERROR,
)

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

    def __init__(self):
        self.addr = "0.0.0.0"
        self.port = 9000
        self.getaddrinfo, self.freeaddrinfo = self.load_libc()
        self.libsrt = self.load_srt()
        self.startup()
        self.sock = self.create_socket()
        self.peer_sock = None
        self.sa_ptr, self.sa_size = self.mk_sockaddr_ptr()

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
            sys.exit(1)
        return libsrt

    def accept(self):
        """
        accept srt_accept
        """
        self.libsrt.srt_accept.argtypes = [
            ctypes.c_int,
            ctypes.POINTER(sockaddr),
            ctypes.POINTER(ctypes.c_int),
        ]
        self.libsrt.srt_accept.restype = ctypes.c_int
        their_addr = sockaddr_storage()
        addr_size = ctypes.c_int(ctypes.sizeof(their_addr))
        self.peer_sock = self.libsrt.srt_accept(
            self.sock, ctypes.byref(their_addr), ctypes.byref(addr_size)
        )
        self.getlasterror()
        if self.peer_sock == SRT_INVALID_SOCK:
            self._close()
            self.cleanup()

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

    def close(self):
        """
        close srt_close
        """
        self.libsrt.srt_close.argtypes = [ctypes.c_int]
        self.libsrt.srt_close.restype = ctypes.c_int
        self.libsrt.srt_close(self.sock)
        self.getlasterror()

    def connect(self, host, port):
        """
        connect connect to  host on port
        """
        hints = addrinfo(ai_family=AF_INET, ai_socktype=SOCK_DGRAM)
        peer = ctypes.POINTER(addrinfo)()
        if (
            self.getaddrinfo(
                host.encode("utf-8"),
                port.encode("utf-8"),
                ctypes.byref(hints),
                ctypes.byref(peer),
            )
            != 0
        ):
            print(f"getaddrinfo failed for {server_ip}:{server_port}", file=sys.stderr)
            return -1
        self.libsrt.srt_connect(
            self.sock, peer.contents.ai_addr, peer.contents.ai_addrlen
        )
        self.freeaddrinfo(peer)
        self.getlasterror()

    def create_socket(self):
        """
        create_socket srt_create_socket
        and return it
        """
        self.libsrt.srt_create_socket.argtypes = []
        self.libsrt.srt_create_socket.restype = ctypes.c_int
        ss = self.libsrt.srt_create_socket()
        self.getlasterror()
        return ss

    def getlasterror(self):
        """
        getlasterror srt_getlasterror_str

        **** I realize it will set argtypes and restype repeatedly
        and I say it doesn't matter.
        """
        self.libsrt.srt_getlasterror_str.argtypes = []
        self.libsrt.srt_getlasterror_str.restype = ctypes.c_char_p
        caller = inspect.currentframe().f_back.f_code.co_name
        print(
            f"{caller}: {self.libsrt.srt_getlasterror_str().decode()}", file=sys.stderr
        )

    def listen(self):
        """
        listen srt_listen
        """
        self.libsrt.srt_listen.argtypes = [ctypes.c_int, ctypes.c_int]
        self.libsrt.srt_listen.restype = ctypes.c_int
        self.libsrt.srt_listen(self.sock, 2)
        self.getlasterror()

    def recv(self):
        """
        recv srt_recv
        """
        buffer_size = 20
        buffer = ctypes.create_string_buffer(buffer_size)
        self.libsrt.srt_recv(self.sock, buffer, ctypes.sizeof(buffer))
        filesize = int.from_bytes(buffer.value, byteorder="little")
        self.getlasterror()
        return filesize

    def recvfile(self, local_filename):
        """
        recvfile srt_recvfile
        """
        filesize = self.recv()
        offset_val = ctypes.c_int64(0)
        recvd_size = self.libsrt.srt_recvfile(
            self.sock,
            local_filename.encode("utf-8"),
            ctypes.byref(offset_val),
            filesize,
            SRT_DEFAULT_RECVFILE_BLOCK,
        )
        self.getlasterror()

    def recvmsg(self):
        """
        recvmsg srt_recvmsg
        """
        self.libsrt.srt_recvmsg.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.libsrt.srt_recvmsg.restype = ctypes.c_int

    def send(self, msg):
        """
        send srt_send
        """
        self.libsrt.srt_send(self.sock, msg, ctypes.sizeof(msg))
        self.getlasterror()

    def sendmsg2(self, msg):
        """
        sendmsg2 format byte string for C
        and write it to the socket
        """
        msg = self.bytemsg(msg)
        st = self.libsrt.srt_sendmsg2(self.sock, msg, ctypes.sizeof(msg), None)
        self.getlasterror()

    def setsockflag(self, flag, val):
        """
        setsockflag  setsockflag
        the flag is one from statiic.SRT_SOCKOPTS
        flag is set to val
        """
        self.libsrt.srt_setsockflag.argtypes = [
            ctypes.c_int,
            ctypes.c_int32,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        self.libsrt.srt_setsockflag.restype = ctypes.c_int
        if self.sock:
            self.libsrt.srt_setsockflag(
                self.sock, flag, ctypes.byref(val), ctypes.sizeof(val)
            )
        else:
            print("if you want to add a flag, make a socket first")
        self.getlasterror()

    def startup(self):
        """
        startup  srt_startup()
        """
        self.libsrt.srt_startup.argtypes = []
        self.libsrt.srt_startup.restype = None
        self.libsrt.srt_startup()
        self.getlasterror()

    # helper methiods not in libsrt

    def ipv4int(self, addr):
        """
        take a ipv4 string addr and make it an int
        """
        sa = int.from_bytes(socket.inet_pton(socket.AF_INET, addr), byteorder="little")
        return sa

    def mk_sockaddr_ptr(self):
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

    def bytemsg(self, msg):
        """
        bytemsg convert python byte string
        to a C string buffer
        """
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
        )  # remote file length written to a string buffer
        self.send(rflen)
        self.send(msg)
        self.getlasterror()

    def fetch(self, host, port, remote_file, local_file):
        """
        fetch fetch remote_file fron host on port
        and save it as local_file

        all args are strings.
        """
        yes = ctypes.c_int(1)
        self.setsockflag(SRTO_TRANSTYPE, yes)
        self.connect(host, port)
        self.request_file(remote_file)
        self.recvfile(local_file)
        self.close()
        self.cleanup()
