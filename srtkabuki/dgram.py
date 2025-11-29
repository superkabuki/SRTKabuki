#!/usr/bin/env python3

"""
dgram.py

Home of the datagramer function.

"""


import sys
import time
from functools import partial
from .srtkabuki import SRTKabuki


PACKETSIZE = 188
BUFFSIZE = 1456
SYNC_BYTE = b"G"
SPIN = True


def _has_sync_byte(stuff):
    """
    _has_sync_byte check stuff for sync_byte
    """
    return stuff[0:1] == SYNC_BYTE


def _at_least_a_packet(stuff):
    """
    _at_least_a_packet  check if stuff  is at least PACKETSIZE
    """
    return len(stuff) >= PACKETSIZE


def _packetize(datagram):
    """
    _packetize split datagram into mpegts packets
    """
    return [datagram[i : i + PACKETSIZE] for i in range(0, len(datagram), PACKETSIZE)]


def _preflight(srt_url):
    """
    _preflight init SRTKabuki instance,
    a buffer, and a threefive.Stream instance
    """
    kabuki = SRTKabuki(srt_url)
    kabuki.connect()
    buffer = kabuki.mkbuff(BUFFSIZE)
    return kabuki, buffer


def _onedgram(kabuki, buffer):
    """
    onedgram receive one datagram
    """
    st = kabuki.recv(buffer)
    datagram = buffer.raw
    buffer = kabuki.mkbuff(BUFFSIZE)
    return datagram


def datagramer(srt_url):
    """
    datagramer datagram generator
    take a live srt_url
    and return datagrams
    """
    kabuki, buffer = _preflight(srt_url)
    datagram = b""
    return iter(partial(_onedgram, kabuki, buffer), b"")


if __name__ == "__main__":
    dc = 0
    srt_url = sys.argv[1]
    for datagram in datagramer(srt_url):
        dc += 1
        print(f"{dc} datagrams length {len(datagram)} bytes")
