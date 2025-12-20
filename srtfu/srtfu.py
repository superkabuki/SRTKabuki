"""
srtfu.py

"""

import ctypes
import ctypes.util
import os
import sys
import time
import socket
import inspect


from . import SRT_DEFAULT_RECVFILE_BLOCK, SRT_LIVE, SRT_FILE
from . import SRTO_TRANSTYPE, SRTO_CONGESTION

# Socket Address structures

SYNC_BYTE = b"G"
PKTSZ = 188


class sockaddr(ctypes.Structure):
    _fields_ = [
        ("sa_family", ctypes.c_ushort),
        ("sa_data", ctypes.c_char * 14),  # 14 bytes for address data
    ]


class in_addr(ctypes.Structure):
    """
    in_addr  struct for ipv4
    """

    _fields_ = [("s_addr", ctypes.c_uint32)]  # IPv4


class sockaddr_in(ctypes.Structure):
    """
    sockaddr_in socketaddr_in struct
    """

    _fields_ = [
        ("sin_family", ctypes.c_short),
        ("sin_port", ctypes.c_ushort),
        ("sin_addr", in_addr),
        ("sin_zero", ctypes.c_char * 8),
    ]


class sockaddr_in6(ctypes.Structure):  # For IPv6
    """
    sockaddr_in6 socketaddr_in6 struct
    """

    _fields_ = [
        ("sin6_family", ctypes.c_ushort),
        ("sin6_port", ctypes.c_ushort),
        ("sin6_flowinfo", ctypes.c_uint),
        ("sin6_addr", ctypes.c_ubyte * 16),
        ("sin6_scope_id", ctypes.c_uint),
    ]


class addrinfo(ctypes.Structure):
    """
    addrinfo Forward declaration
    for self-referential pointer and stuff.
    I don't know why.
    """

    pass


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
    """
    sockaddr_storage yet another struct to match
    a c struct.
    """

    _fields_ = [
        ("ss_family", ctypes.c_ushort),
        (
            "ss_data",
            ctypes.c_ubyte * (128 - ctypes.sizeof(ctypes.c_ushort)),
        ),
    ]


class SRTfu:
    """
    SRTfu Pythonic Secure Reliable Transport
    """

    def __init__(self, srturl, flags=None):
        self.addr, self.port, self.path, self.args = self.split_url(srturl)
        self.getaddrinfo, self.freeaddrinfo = self.load_libc()
        self.libsrt = self.load_srt()
        self.startup()
        self.sa_ptr, self.sa_size = self.mk_sockaddr_ptr(self.addr, self.port)
        self.sock = self.create_socket()
        if flags:
            self.setflags(flags)
        self.peer_addr = None
        self.peer_addr_size = None
        self.peer_sock = None
        self.eid = None

    @staticmethod
    def split_url(url):
        """
        split_url, split srt url into addr,port, path and args
        """
        addr = port = path = args = None
        url = url.replace("srt://", "")
        if "?" in url:
            url, args = url.split("?")
        if "/" in url:
            url, path = url.split("/", 1)
        addr, port = url.split(":", 1)
        return addr, int(port), path, args

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
        path=f'{os.path.dirname(__file__)}/libsrt.so'
        try:
            libsrt = ctypes.CDLL(path)
        except:
            # raise OSError("failed to load libsrt.so")
            print('... building libsrt real quick', file=sys.stderr)
            from .libsrtinstall import libsrtinstall
            libsrtinstall()
            path=f'{os.path.dirname(__file__)}/libsrt.so'
            libsrt = ctypes.CDLL(path)
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

    def congestion_control(self, algo):
        """
        congestion_control set the congestion control
        algorithm. can also be set with livecc() and filecc()
        methods.
        """
        self.setsockflag(SRTO_CONGESTION, algo)

    def conlive(self):
        """
        conlive set congestion control to live
        """
        self.congestion_control("live")
        self.getlasterror()

    def confile(self):
        """
        confile set congestion control to file
        """
        self.congestion_control("file")
        self.getlasterror()

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

    def epoll_wait(self, readfds, writefds, ms_timeout, lrfds, lwfds):
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
        out = f"{caller}: {self.libsrt.srt_getlasterror_str().decode()}".replace(
            "Success", "✓"
        )
        print(out, file=sys.stderr)

    def getsockstate(self, sock=None):
        """
        getsockstate srt_getsockstate
        """
        sockstatus = [
            None,
            "SRTS_INIT",
            "SRTS_OPENED",
            "SRTS_LISTENING",
            "SRTS_CONNECTING",
            "SRTS_CONNECTED",
            "SRTS_BROKEN",
            "SRTS_CLOSING",
            "SRTS_CLOSED",
            "SRTS_NONEXIST",
        ]
        sock = self.chk_sock(sock)
        print(
            "SOCK STATE ",
            sockstatus[self.libsrt.srt_getsockstate(sock)],
            " for sock ",
            sock,
            file=sys.stderr,
        )
        self.getlasterror()

    def ipv4int(self, addr):
        """
        take a ipv4 string addr and make it an int
        """
        sa = int.from_bytes(socket.inet_pton(socket.AF_INET, addr), byteorder="little")
        self.getlasterror()
        return sa

    def listen(self):
        """
        listen srt_listen
        """
        self.libsrt.srt_listen(self.sock, 2)
        self.getlasterror()

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

    def mkbuff(self, buffsize, data=b""):
        """
        mkbuff make a c  buffer
        to read into when receiving data.
        """
        return ctypes.create_string_buffer(data, buffsize)

    def mkmsg(self, msg):
        """
        mkmsg convert python byte string
        to a C string buffer when sending data
        """
        if not isinstance(msg, (bytes, str)):
            msg = str(msg)
        if isinstance(msg, str):
            msg = msg.encode("utf8")
        if not isinstance(msg, bytes):
            msg = b"Message needs to be bytes"
        return self.mkbuff(len(msg), msg)

    def new_val(self, val):
        """
        new_val convert val into a ctypes type
        """
        nval = None
        if isinstance(val, int):
            nval = ctypes.c_int(val)
        if isinstance(val, bool):
            nval = ctypes.c_bool(val)
        if isinstance(
            val,
            (
                str,
                bytes,
            ),
        ):
            nval = self.mkmsg(val)
        return nval

    def read(self, numbytes):
        """
        read read numbytes of bytes
        and return them.
        """
        buffsize = 1500
        bigfatbuff = b""
        newbuff = b""
        while numbytes > 0:
            buff = self.mkbuff(buffsize)
            self.recv(buff)
            numbytes -= buffsize
            bigfatbuff += buff.raw
            while SYNC_BYTE in bigfatbuff:
                bigfatbuff = bigfatbuff[bigfatbuff.index(SYNC_BYTE) :]
                packet, bigfatbuff = bigfatbuff[:PKTSZ], bigfatbuff[PKTSZ:]
                if packet.startswith(SYNC_BYTE):
                    newbuff += packet
        return newbuff

    def recv(self, buffer, sock=None):
        """
        recv srt_recv
        """
        sock = self.chk_sock(sock)
        st = self.libsrt.srt_recv(sock, buffer, len(buffer))
        return st

    def recvfile(self, local_file, sock=None):
        """
        recvfile srt_recvfile
        """
        sock = self.chk_sock(sock)
        remote_size = self.remote_file_size()
        print("remote size recv", remote_size, file=sys.stderr)
        offset_val = 0
        recvsize = self.libsrt.srt_recvfile(
            sock,
            local_file.encode("utf-8"),
            ctypes.byref(ctypes.c_int64(offset_val)),
            ctypes.c_int64(remote_size),
            SRT_DEFAULT_RECVFILE_BLOCK,
        )
        self.getlasterror()
        print("recvsize", recvsize, file=sys.stderr)
        return recvsize

    def recvmsg(self, buffer, sock=None):
        """
        recvmsg srt_recvmsg
        """
        sock = self.chk_sock(sock)
        st = self.libsrt.srt_recvmsg(sock, buffer, len(buffer))
        return st

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
        print(filename, file=sys.stderr)
        sock = self.chk_sock(sock)
        filesize = os.path.getsize(filename)
        print("sendfile size ", filesize, file=sys.stderr)
        msg = str(filesize).encode("utf8")
        msgbuff = self.mkmsg(msg)
        self.send(msgbuff, sock)
        self.getlasterror()
        offset = ctypes.c_int64(0)
        self.libsrt.srt_sendfile(
            sock,
            filename,
            ctypes.byref(offset),
            ctypes.c_int64(filesize),
            SRT_DEFAULT_RECVFILE_BLOCK,
        )
        self.getlasterror()

    def sendmsg2(self, msg, sock=None):
        """
        sendmsg2 srt_sendmsg2
        """
        sock = self.chk_sock(sock)
        msg = self.mkmsg(msg)
        self.libsrt.srt_sendmsg2(sock, msg, 32, None)
        self.getlasterror()
        time.sleep(0.001)

    def setsockflag(self, flag, val):
        """
        setsockflag  srt_setsockflag
        """
        nval = self.new_val(val)
        st = self.libsrt.srt_setsockflag(
            self.sock, flag, ctypes.byref(nval), ctypes.sizeof(nval)
        )
        self.getlasterror()

    def setflags(self, flags):
        """
        setflags set flags on an SRTfu instance

        flags  a dict of socket flags you want to have set.
                   ex. {SRTO_TRANSTYPE: SRT_LIVE,
                           SRTO_RCVSYN: 1, }
        """
        for k, v in flags.items():
            self.setsockflag(k, v)
            self.getlasterror()

    def startup(self):
        """
        startup  srt_startup()
        """
        self.libsrt.srt_startup()
        self.getlasterror()

    # helper methods not in libsrt

    def remote_file_size(self):
        """
        remote_file_size read remote file size.
        """
        buffer_size = 20
        buffer = self.mkbuff(buffer_size)
        self.recv(buffer)
        print("buffer.value ", buffer.value, file=sys.stderr)
        try:
            file_size = int(buffer.value.decode())
        except:
            file_size = 0
        print("remote file size", file_size, file=sys.stderr)
        self.getlasterror()
        return file_size

    def request_file(self, remote_file):
        """
        request_file request a file from a server
        """
        remote_filename = remote_file.encode("utf8")
        msg = self.mkmsg(remote_filename)
        rfl = bytes(
            [
                len(remote_filename),
            ]
        )  # remote file length
        print("rfl", rfl, file=sys.stderr)
        rflen = self.mkmsg(rfl)
        self.send(rflen, self.sock)
        self.getlasterror()
        self.send(msg, self.sock)
        self.getlasterror()

    def fetch(self, remote_file, local_file):
        """
        fetch fetch remote_file fron host on port
        and save it as local_file
        """
        self.setsockflag(SRTO_TRANSTYPE, SRT_FILE)
        self.connect()
        self.request_file(remote_file)
        self.recvfile(local_file)

    def chk_sock(self, sock=None):
        """
        chk_sock if we don't have a sock, use self.sock
        """
        if not sock:
            sock = self.sock
        return sock
