#!/usr/bin/env python3

import ctypes
import sys
import socket
import time

YES = 1
SRTO_SENDER = 21
PORT = 9000
ADDR = "127.0.0.1"
SRTO_RCVSYN = 2




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

# Example usage:
# import socket
# hints = {"ai_family": socket.AF_INET, "ai_socktype": socket.SOCK_STREAM}
# addresses = get_addr_info_ctypes("localhost", 80, hints)
# print(addresses)



class SRTKabuki:

    def __init__(self,addr,port):
        self.addr=addr
        self.port=port
        self.mesg=None
        self.file=None
        self.libsrt = ctypes.CDLL("libsrt.so")
        self.libsrt.srt_getlasterror_str.restype = ctypes.c_char_p
        self.libsrt.srt_startup()
        self.sa_ptr, self.sa_size = self.mk_sockaddr_ptr()
        print(f"SRTKabuki  mk_sockaddr_ptr: {self.libsrt.srt_getlasterror_str()}")
        self.sock = self.libsrt.srt_create_socket()
        print(f"libsrt srt_create_socket: {self.libsrt.srt_getlasterror_str()}")

    def set_sock_flag(self,flag):
        self.libsrt.srt_setsockflag(self.sock, flag, 1, 32)
        print(f"SRTKabuki set_sock_flag: {self.libsrt.srt_getlasterror_str()}")

    def bind(self):
        """
        bind is srt_bind()
        """
        self.libsrt.srt_bind(self.sock, self.sa_ptr, 64)
        print(f"libsrt srt_bind: {self.libsrt.srt_getlasterror_str()}")
       
    def connect(self):
        """
        connect  is srt_connect()
        """
        self.libsrt.srt_connect(self.sock, self.sa_ptr, 64)
        print(f"libsrt srt_connect: {self.libsrt.srt_getlasterror_str()}")

    def listen(self):
        self.libsrt.srt_listen(self.sock, 2)
        print(f"libsrt srt_listen: {self.libsrt.srt_getlasterror_str()}")

    def done(self):
        """
        done close the socket and call cleanup.
        """
        self.libsrt.srt_close(self.sock)
        self.libsrt.srt_cleanup()
        print(f"SRTKabuki  done: {self.libsrt.srt_getlasterror_str()}")

    def send_mesg(self,mesg):
        """
        send_mesg format byte string for C
        and write it to the socket
        """
        mesg = self.byte_mesg(mesg)
        st = self.libsrt.srt_sendmsg2(self.sock, mesg, ctypes.sizeof(mesg), None)
        if st:

            print(f"SRTKabuki  send_mesg: {self.libsrt.srt_getlasterror_str()}")
        time.sleep(0.1)

    def  byte_mesg(self,mesg):
        """
        byte_mesg convert python byte string
        to a C string buffer
        """
        if not isinstance(mesg,bytes):
            mesg =b"Message needs to be bytes"
        return ctypes.create_string_buffer(mesg,len(mesg))

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

    def mk_client_sockaddr_ptr(self):
        """
        mk_sockaddr_sa make a c compatible (struct sockaddr*)&sa for client 
        """
        sa_client = sockaddr_in()
        sa_client.sin_family = socket.AF_INET
        sa_client.sin_port = socket.htons(self.port)
        sa_client.sin_addr.s_addr = self.ipv4int("0.0.0.0")  #socket.INADDR_ANY
        sa_client_ptr=ctypes.pointer(sa_client)
        return ctypes.cast(sa_client_ptr, ctypes.POINTER(sockaddr)), ctypes.sizeof(sa_client)


def send_mesg(addr,port,mesg):
    srtk=SRTKabuki(addr,port)
    srtk.set_sock_flag(SRTO_SENDER)
    srtk.connect()
    a =100
    while a:
        a -=1
        srtk.send_mesg(b'I am super cool')
        time.sleep(0.1)
 #   time.sleep(1)
    srtk.done()
    

def  mesg_server(addr,port):
    libc = ctypes.CDLL("libc.so.6") # Linux
    libc.getaddrinfo.argtypes = [
    ctypes.c_char_p, # node
    ctypes.c_char_p, # service
    ctypes.POINTER(addrinfo), # hints
    ctypes.POINTER(ctypes.POINTER(addrinfo)) # res
]
    libc.getaddrinfo.restype = ctypes.c_int
    libc.freeaddrinfo.argtypes = [ctypes.POINTER(addrinfo)]
    libc.freeaddrinfo.restype = None
    hints=addrinfo()
    res = addrinfo()
    hints.ai_flags = socket.AI_PASSIVE;
    hints.ai_family = socket.AF_INET;
    hints.ai_socktype = socket.SOCK_DGRAM;    
    srtk=SRTKabuki(addr,port)
   # srtk.set_sock_flag(SRTO_RCVSYN)     # use this for non-blocking
    srtk.bind()
    srtk.listen()
    client_sa_ptr, client_sa_size= srtk.mk_client_sockaddr_ptr()
    print(f"SRTKabuki  mk_client_sockaddr_ptr: {srtk.libsrt.srt_getlasterror_str()}")

    client_sock = srtk.libsrt.srt_accept(srtk.sock,client_sa_ptr,client_sa_size)
    print(f"libsrt srt_accept: {srtk.libsrt.srt_getlasterror_str()}")


if __name__=="__main__":
    mesg_server("0.0.0.0",9000)
