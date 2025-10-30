"""
srtkabuki.py

"""

import ctypes
import inspect
import socket
import sys
import time

SRTO_RCVSYN = 29

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


class sockaddr_in6(ctypes.Structure): # For IPv6
    _fields_ = [
        ("sin6_family", ctypes.c_ushort),
        ("sin6_port", ctypes.c_ushort),
        ("sin6_flowinfo", ctypes.c_uint),
        ("sin6_addr", ctypes.c_ubyte * 16),
        ("sin6_scope_id", ctypes.c_uint)
    ]


class addrinfo(ctypes.Structure):
    pass # Forward declaration for self-referential pointer

addrinfo._fields_ = [
    ("ai_flags", ctypes.c_int),
    ("ai_family", ctypes.c_int),
    ("ai_socktype", ctypes.c_int),
    ("ai_protocol", ctypes.c_int),
    ("ai_addrlen", ctypes.c_size_t),
    ("ai_addr", ctypes.POINTER(sockaddr)),
    ("ai_canonname", ctypes.c_char_p),
    ("ai_next", ctypes.POINTER(addrinfo))
]


class sockaddr_storage(ctypes.Structure):
    _fields_ = [
        ("ss_family", ctypes.c_ushort),
        ("ss_data", ctypes.c_ubyte * (128 - ctypes.sizeof(ctypes.c_ushort))), # Example size, adjust as needed
    ]


def get_addr_info_ctypes(host, port, hints=None):
    node = host.encode('utf-8') if host else None
    service = str(port).encode('utf-8') if port else None
    hints_ptr = None
    if hints:
        # Create a hints addrinfo structure
        c_hints = addrinfo()
        c_hints.ai_family = hints.get("ai_family", 0)
        c_hints.ai_socktype = hints.get("ai_socktype", 0)
        c_hints.ai_protocol = hints.get("ai_protocol", 0)
        c_hints.ai_flags = hints.get("ai_flags", 0)
        hints_ptr = ctypes.pointer(c_hints)
    res_ptr = ctypes.POINTER(addrinfo)()
    err = libc.getaddrinfo(node, service, hints_ptr, ctypes.byref(res_ptr))
    if err != 0:
        # Handle error (e.g., raise an exception)
        raise OSError(f"getaddrinfo failed with error: {err}")
    results = []
    current = res_ptr.contents
    while True:
        # Process the current addrinfo structure
        # Extract family, socktype, protocol, address, etc.
        # Example:
        # if current.ai_family == AF_INET:
        #     sockaddr_data = ctypes.cast(current.ai_addr, ctypes.POINTER(sockaddr_in)).contents
        #     ip_address = ".".join(map(str, sockaddr_data.sin_addr))
        #     port_number = socket.ntohs(sockaddr_data.sin_port)
        #     results.append({"family": current.ai_family, "address": ip_address, "port": port_number})
        if not current.ai_next:
            break
        current = current.ai_next.contents
    libc.freeaddrinfo(res_ptr) # Free the allocated memory
    return results



class SRTKabuki:

    def __init__(self):
        self.addr='0.0.0.0'
        self.port=9000
        self.libsrt = self.load_so()
        self.startup()
        self.sock = self.mk_sock()
        self.sa_ptr, self.sa_size = self.mk_sockaddr_ptr()


    def load_so(self):
        """
        load_so load libsrt.so
        """
        libsrt = None
        libsrt = ctypes.CDLL("libsrt.so")
        if not libsrt:
            raise OSError("failed to load libsrt.so")
            sys.exit(1)
        return libsrt

    def ipv4int(self,addr):
        """
        take a ipv4 string addr and make it an int
        """
        sa = int.from_bytes(socket.inet_pton(socket.AF_INET, addr), byteorder="little")
        print(f"SA {sa}")
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

    def set_sock_flag(self, flag,val):
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
            self.libsrt.srt_setsockflag(self.sock, flag, 1, 32)
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
        self.libsrt.srt_connect(self.sock, self.sa_ptr,self.sa_size )
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

    def  byte_mesg(self,mesg):
        """
        byte_mesg convert python byte string
        to a C string buffer
        """
        if not isinstance(mesg,bytes):
            mesg =b"Message needs to be bytes"
        return ctypes.create_string_buffer(mesg,len(mesg))
    
    def send_mesg(self,mesg):
        """
        send_mesg format byte string for C
        and write it to the socket
        """
        mesg = self.byte_mesg(mesg)
        st = self.libsrt.srt_sendmsg2(self.sock, mesg, ctypes.sizeof(mesg), None)


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
