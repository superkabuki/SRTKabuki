"""
srtkabuki.py

"""

import ctypes
import ctypes.util
import sys
import os
import socket
import struct


from static import (
    SRT_DEFAULT_RECVFILE_BLOCK,
    SRTO_TRANSTYPE,
    SOCK_DGRAM,
    AF_INET,
    AI_PASSIVE,
    SRT_ERROR,
)

# SRTO_RCVSYN = 29

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
        self.sock = self.mk_sock()
        self.sa_ptr, self.sa_size = self.mk_sockaddr_ptr()

    @staticmethod
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

    @staticmethod
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

    def startup(self):
        """
        startup  srt_startup()
        """
        self.libsrt.srt_startup.argtypes = []
        self.libsrt.srt_startup.restype = None
        self.libsrt.srt_startup()
        self.last_error()

    def last_error(self):
        """
        last_error srt_getlasterror_str

        **** I realize it will set argtypes and restype repeatedly
        and I say it doesn't matter.
        """
        self.libsrt.srt_getlasterror_str.argtypes = []
        self.libsrt.srt_getlasterror_str.restype = ctypes.c_char_p
        caller = inspect.currentframe().f_back.f_code.co_name
        print(
            f"{caller}: {self.libsrt.srt_getlasterror_str().decode()}", file=sys.stderr
        )

    def create_socket(self):
        """
        create_socket srt_create_socket
        and return it
        """
        self.libsrt.srt_create_socket.argtypes = []
        self.libsrt.srt_create_socket.restype = ctypes.c_int
        ss = libsrt.srt_create_socket()
        self.last_error()
        return ss

    def set_sock_flag(self, flag, val):
        """
        set_sock_flag  set_sock_flag
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
            self.libsrt.srt_setsockflag(self.sock, flag,  ctypes.byref(val), ctypes.sizeof(val))
        else:
            print("if you want to add a flag, make a socket first")
        self.last_error()

    def bind(self):
        """
        bind  srt_bind
        """
        self.libsrt.srt_bind.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
        self.libsrt.srt_bind.restype = ctypes.c_int
        self.libsrt.srt_bind(self.sock, self.sa_ptr, self.sa_size)
        self.last_error()

    def listen(self):
        """
        listen srt_listen
        """
        self.libsrt.srt_listen.argtypes = [ctypes.c_int, ctypes.c_int]
        self.libsrt.srt_listen.restype = ctypes.c_int
        self.libsrt.srt_listen(self.sock, 2)
        self.last_error()

    def connect(self):
        """
        connect  is srt_connect()
        """
        self.libsrt.srt_connect(self.sock, self.sa_ptr, self.sa_size)
        self.last_error()

    def accept(self):
        """
        accept srt_accept
        """
        self.libsrt.srt_accept.argtypes = [
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_int),
        ]
        self.libsrt.srt_accept.restype = ctypes.c_int

    def recvmsg(self):
        """
        recvmsg srt_recvmsg
        """
        self.libsrt.srt_recvmsg.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int]
        self.libsrt.srt_recvmsg.restype = ctypes.c_int

    def byte_mesg(self, mesg):
        """
        byte_mesg convert python byte string
        to a C string buffer
        """
        if not isinstance(mesg, bytes):
            mesg = b"Message needs to be bytes"
        return ctypes.create_string_buffer(mesg, len(mesg))

    def send_mesg(self, mesg):
        """
        send_mesg format byte string for C
        and write it to the socket
        """
        mesg = self.byte_mesg(mesg)
        st = self.libsrt.srt_sendmsg2(self.sock, mesg, ctypes.sizeof(mesg), None)
        self.last_error()

    def send(self, mesg):
        """
        send srt_send
        """
        self.libsrt.srt_send(self.sock, mesg, ctypes.sizeof(mesg))
        self.last_error()

    def close(self):
        """
        close srt_close
        """
        self.libsrt.srt_close.argtypes = [ctypes.c_int]
        self.libsrt.srt_close.restype = ctypes.c_int

    def cleanup(self):
        """
        cleanup srt_cleanup
        """
        self.libsrt.srt_cleanup.argtypes = []
        self.libsrt.srt_cleanup.restype = None

    def request_file(self, remote_file):
        remote_filename = remote_file.encode("utf8")
        mesg = ctypes.create_string_buffer(remote_filename, len(remote_filename))
        rfl = str(len(remote_filename)).encode("utf8")  # remote file length
        rflen = ctypes.create_string_buffer(
            rfl, len(rfl)
        )  # remote file length written to a string buffer
        self.libsrt.srt_send(self.sock, rflen, ctypes.sizeof(ctypes.c_int(len(mesg))))
        self.libsrt.srt_send(self.sock, mesg, len(mesg))
        self.last_error()

    def remote_file_size(self):
        buffer_size = 20
        buffer = ctypes.create_string_buffer(buffer_size)
        self.libsrt.srt_recv(self.sock, buffer, ctypes.sizeof(buffer))
        file_size = int.from_bytes(buffer.value, byteorder="little")
        self.last_error()
        return file_size

    def fetch(self, host, port, remote_file, local_file):
        yes = ctypes.c_int(1)
        self.set_sock_flag(SRTO_TRANSTYPE,yes)
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
        self.request_file(remote_file)
        remote_size = self.remote_file_size()
        offset_val = ctypes.c_int64(0)
        recvsize = self.libsrt.srt_recvfile(
            self.sock,
            local_file.encode("utf-8"),
            ctypes.byref(offset_val),
            remote_size,
            SRT_DEFAULT_RECVFILE_BLOCK,
        )
        self.last_error()
