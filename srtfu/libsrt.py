'''
libsrt.py
Most of libsrt mapped to ctypes
'''

import ctypes
import ctypes.util
import sys
import os
import socket
import struct

try:
    libsrt = ctypes.CDLL(ctypes.util.find_library("srt"))
except OSError:
    print("Error: Could not find libsrt.so . Please ensure SRT is installed and accessible.", file=sys.stderr)
    sys.exit(1)

# Handle sizeof args like this
intsize = ctypes.sizeof(ctypes.c_int)


# Load the C standard library for getaddrinfo
libc = ctypes.CDLL(ctypes.util.find_library('c'))

# Constants and types
SRTSOCKET = ctypes.c_int
SRT_ERROR = -1
AF_INET = socket.AF_INET
SOCK_DGRAM = socket.SOCK_DGRAM
AI_PASSIVE = socket.AI_PASSIVE

# SRT options
SRT_TRANSTYPE_FILE = 1
SRTO_TRANSTYPE = 50
SRT_DEFAULT_RECVFILE_BLOCK = 7200
SRT_EPOLL_EVENT = ctypes.c_int

# getaddrinfo structs
class sockaddr_in(ctypes.Structure):
    _fields_ = [
        ('sin_family', ctypes.c_ushort),
        ('sin_port', ctypes.c_ushort),
        ('sin_addr', ctypes.c_byte * 4),
        ('sin_zero', ctypes.c_byte * 8)
    ]

class addrinfo(ctypes.Structure):
    pass
addrinfo._fields_ = [
    ('ai_flags', ctypes.c_int),
    ('ai_family', ctypes.c_int),
    ('ai_socktype', ctypes.c_int),
    ('ai_protocol', ctypes.c_int),
    ('ai_addrlen', ctypes.c_size_t),
    ('ai_addr', ctypes.POINTER(sockaddr_in)),
    ('ai_canonname', ctypes.c_char_p),
    ('ai_next', ctypes.POINTER(addrinfo))
]

# sockaddr structure (generic, for functions like srt_bind, srt_accept, etc.)
class sockaddr(ctypes.Structure):
    _fields_ = [
        ('sa_family', ctypes.c_ushort),
        ('sa_data', ctypes.c_byte * 14),
    ]

# SRT_TRACEBSTATS structure
class SRT_TRACEBSTATS(ctypes.Structure):
    _fields_ = [
        ('pktFlowWindow', ctypes.c_int),
        ('pktCongestionWindow', ctypes.c_int),
        ('msRTT', ctypes.c_int),
        ('mbpsRecvRate', ctypes.c_double),
        ('pktRcvLossTotal', ctypes.c_int),
        ('pktRecv', ctypes.c_int),
        # Note: This structure in C has many more fields for detailed stats.
        # These are the basic ones that match common usage.
    ]

# SRT_MSGCTRL structure
class SRT_MSGCTRL(ctypes.Structure):
    _fields_ = [
        ('msgttl', ctypes.c_int),
        ('inorder', ctypes.c_bool),
        ('srctime', ctypes.c_int),
        ('pktseq', ctypes.c_int),
        ('msgno', ctypes.c_int),
        # Other potential fields like 'flags', 'boundary', 'sndmbps', 'rcvmbps', 'maxbw' exist in C++ implementation but may not be in public C API struct definition
    ]

# Structure for srt_epoll_wait events (SRT_EPOLL_EVENT defined as an int type)
class SRT_EPOLL_EVENT_(ctypes.Structure):
    _fields_ = [
        ('fd', SRTSOCKET),
        ('events', ctypes.c_int),
    ]

# SRT_SOCKSTATUS enumeration (represented as an int)
SRT_SOCKSTATUS = ctypes.c_int
SRT_SS_INIT = 0
SRT_SS_OPENED = 1
SRT_SS_LISTENING = 2
SRT_SS_CONNECTING = 3
SRT_SS_CONNECTED = 4
SRT_SS_BROKEN = 5
SRT_SS_CLOSING = 6
SRT_SS_CLOSED = 7
SRT_SS_IDLE = 8
SRT_SS_HANDSHAKE = 9


def wrap_func(name, argtypes, restype):
    """
    wrap_func wrap libsrt function in ctypes and export to top level namespace. 
    """
    try:
        func = getattr(libsrt, name)
        libsrt.func.argtypes = argtypes
        libsrt.func.restype = restype
 

# Core API Functions
srt_startup = wrap_func("srt_startup", [], ctypes.c_int)
srt_cleanup = wrap_func("srt_cleanup", [], ctypes.c_int)
srt_create_socket = wrap_func("srt_create_socket", [], SRTSOCKET)
srt_socket = wrap_func("srt_socket", [ctypes.c_int, ctypes.c_int, ctypes.c_int], SRTSOCKET)
srt_close = wrap_func("srt_close", [SRTSOCKET], ctypes.c_int)
srt_bind = wrap_func("srt_bind", [SRTSOCKET, ctypes.POINTER(sockaddr), ctypes.c_int], ctypes.c_int)
srt_listen = wrap_func("srt_listen", [SRTSOCKET, ctypes.c_int], ctypes.c_int)
srt_connect = wrap_func("srt_connect", [SRTSOCKET, ctypes.POINTER(sockaddr), ctypes.c_int], ctypes.c_int)
srt_accept = wrap_func("srt_accept", [SRTSOCKET, ctypes.POINTER(sockaddr), ctypes.POINTER(ctypes.c_int)], SRTSOCKET)

# Data Transfer
srt_send = wrap_func("srt_send", [SRTSOCKET, ctypes.c_char_p, ctypes.c_int], ctypes.c_int)
srt_recv = wrap_func("srt_recv", [SRTSOCKET, ctypes.c_char_p, ctypes.c_int], ctypes.c_int)
srt_sendmsg = wrap_func("srt_sendmsg", [SRTSOCKET, ctypes.c_char_p, ctypes.c_int], ctypes.c_int)
srt_recvmsg = wrap_func("srt_recvmsg", [SRTSOCKET, ctypes.c_char_p, ctypes.c_int], ctypes.c_int)
srt_sendmsg2 = wrap_func("srt_sendmsg2", [SRTSOCKET, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SRT_MSGCTRL), ctypes.c_int], ctypes.c_int)
srt_recvmsg2 = wrap_func("srt_recvmsg2", [SRTSOCKET, ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(SRT_MSGCTRL), ctypes.c_int], ctypes.c_int)

# Socket Options and Status
srt_getsockopt = wrap_func("srt_getsockopt", [SRTSOCKET, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)], ctypes.c_int)
srt_setsockopt = wrap_func("srt_setsockopt", [SRTSOCKET, ctypes.c_int, ctypes.c_int, ctypes.c_void_p, ctypes.c_int], ctypes.c_int)
srt_getsockflag = wrap_func("srt_getsockflag", [SRTSOCKET, ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_int)], ctypes.c_int)
srt_setsockflag = wrap_func("srt_setsockflag", [SRTSOCKET, ctypes.c_int, ctypes.POINTER(ctypes.c_int), ctypes.c_int], ctypes.c_int)
srt_getsockname = wrap_func("srt_getsockname", [SRTSOCKET, ctypes.POINTER(sockaddr), ctypes.POINTER(ctypes.c_int)], ctypes.c_int)
srt_getpeername = wrap_func("srt_getpeername", [SRTSOCKET, ctypes.POINTER(sockaddr), ctypes.POINTER(ctypes.c_int)], ctypes.c_int)
srt_getsockstate = wrap_func("srt_getsockstate", [SRTSOCKET], SRT_SOCKSTATUS)

# Error Handling
srt_getlasterror = wrap_func("srt_getlasterror", [ctypes.POINTER(ctypes.c_int)], ctypes.c_int)
srt_getlasterror_str = wrap_func("srt_getlasterror_str", [ctypes.POINTER(ctypes.c_int)], ctypes.c_char_p)
srt_clearlasterror = wrap_func("srt_clearlasterror", [], None) # Returns void

# Statistics
srt_bstats = wrap_func("srt_bstats", [SRTSOCKET, ctypes.POINTER(SRT_TRACEBSTATS), ctypes.c_bool, ctypes.c_bool], ctypes.c_int) # clear and link

# Epoll
srt_epoll_create = wrap_func("srt_epoll_create", [], ctypes.c_int)
srt_epoll_add_usock = wrap_func("srt_epoll_add_usock", [ctypes.c_int, SRTSOCKET, ctypes.POINTER(ctypes.c_int)], ctypes.c_int)
srt_epoll_uwait = wrap_func("srt_epoll_uwait", [ctypes.c_int, ctypes.POINTER(SRT_EPOLL_EVENT_), ctypes.c_int, ctypes.c_long], ctypes.c_int)
# srt_epoll_wait ..... pass
srt_epoll_release = wrap_func("srt_epoll_release", [ctypes.c_int], ctypes.c_int)
srt_epoll_remove_usock = wrap_func("srt_epoll_remove_usock", [ctypes.c_int, SRTSOCKET], ctypes.c_int)

# Versioning and Logging
srt_getversion = wrap_func("srt_getversion", [], ctypes.c_int) # returns integer version code
srt_setloglevel = wrap_func("srt_setloglevel", [ctypes.c_int], None)
# srt_setloghandler ..... pass

