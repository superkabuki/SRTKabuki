"""
srtkabuki.py

"""

import ctypes
import inspect

SRTO_RCVSYN = 29


class SRTKabuki:

    def __init__(self):
        self.libsrt = self.load_so()
        self.startup()
        self.sock = self.mk_sock()

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

    def set_sock_flag(self, flag):
        """
        set_sock_flag  set_sock_flag
        """
        self.libsrt.srt_setsockflag.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.c_int,
        ]
        self.libsrt.srt_setsockflag.restype = ctypes.c_int
        if self.sock:
            self.libsrt.srt_setsockflag(self.sock, flag, 1, 32)
        else:
            print("if you want to add a flag, make a socket first")
        self.last_error()

    def bind(self):
        """
        bind  srt_bind
        """
        self.libsrt.srt_bind.argtypes = [ctypes.c_int, ctypes.c_void_p, ctypes.c_int]
        self.libsrt.srt_bind.restype = ctypes.c_int

    def listen(self):
        """
        listen srt_listen
        """
        self.libsrt.srt_listen.argtypes = [ctypes.c_int, ctypes.c_int]
        self.libsrt.srt_listen.restype = ctypes.c_int

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
