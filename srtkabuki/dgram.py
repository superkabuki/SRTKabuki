#!/usr/bin/env python3

"""
dgram.py

Home of the datagramer function.

"""


import sys
import time
from .srtkabuki import SRTKabuki
from .srt_h import SRTO_TRANSTYPE, SRTO_RCVSYN, SRTO_RCVBUF


PACKETSIZE = 188
BUFFSIZE = 1456


def packetizer(srt_url):
    """
    packetizer mpegts packet generator
    """
    for datagram in datagramer(srt_url):
        packets= [datagram[i : i + PACKETSIZE] for i in range(0, len(datagram), PACKETSIZE)]
        for packet in packets:
            yield packet


def preflight(srt_url):
    """
    preflight init SRTKabuki instance,
    and set sock flags as desired.
    """
    SRT_LIVE=0
    kabuki = SRTKabuki(srt_url)
    kabuki.livecc()
    kabuki.setsockflag(SRTO_TRANSTYPE,SRT_LIVE)
    kabuki.setsockflag(SRTO_RCVSYN,1)
    kabuki.setsockflag(SRTO_RCVBUF,32768)
    kabuki.connect()
    return kabuki


def datagramer(srt_url):
    """
    datagramer datagram generator
    take a live srt_url
    and return datagrams
    """
    kabuki = preflight(srt_url)
    while True:
        buffer = kabuki.mkbuff(BUFFSIZE)
        st = kabuki.recv(buffer)
        datagram = buffer.raw
        yield datagram


if __name__ == "__main__":
    dc = 0
    srt_url = sys.argv[1]
    for datagram in datagramer(srt_url):
        dc += 1
        print(f"{dc} datagrams length {len(datagram)} bytes")
