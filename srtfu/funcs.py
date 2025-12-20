"""
funcs.py

Home of the fetch and datagramer functions.

"""

import sys
import time
from .srtfu import SRTfu
from . import SRTO_TRANSTYPE, SRTO_RCVSYN, SRTO_RCVBUF, SRT_LIVE


BUFFSIZE = 1500
PKTSZ = 188
SYNC_BYTE = b"G"
ZERO = b"\x00"


def _preflight(srt_url, flags=None):
    """
    preflight init SRTfu instance,
    and set sock flags as desired.
    """
    srtf = SRTfu(srt_url, flags)
    srtf.conlive()
    srtf.connect()
    return srtf


def datagramer(srt_url, flags=None):
    """
    datagramer datagram generator
    take a live srt_url
    and return datagrams
    """
    preflags = {
        SRTO_TRANSTYPE: SRT_LIVE,
        SRTO_RCVSYN: 1,
        SRTO_RCVBUF: 32768000,
    }
    if flags:
        preflags.update(flags)
    srtf = _preflight(srt_url, preflags)
    while True:
        buffer = srtf.mkbuff(BUFFSIZE)
        st = srtf.recv(buffer)
        datagram = buffer.raw#.rstrip(ZERO)
        yield datagram


def has_sync_byte(stuff):
    """
    has_sync_byte check stuff for sync_byte
    """
    return stuff[0:1] == SYNC_BYTE


def at_least_a_packet(stuff):
    """
    at_least_a_packet  check if stuff  is at least PKTSZ
    """
    return len(stuff) >= PKTSZ


def packetizer(srt_url, flags=None):
    """
    packetizer  mpegts packet generator

    ex.
        for packet in packetizer(srt_url):
            ...
    """
    bigfatbuff = b""
    for datagram in datagramer(srt_url, flags):
        bigfatbuff += datagram
        while SYNC_BYTE in bigfatbuff:
            bigfatbuff = bigfatbuff[bigfatbuff.index(SYNC_BYTE) :]
            packet, bigfatbuff = bigfatbuff[:PKTSZ], bigfatbuff[PKTSZ:]
            if has_sync_byte(packet):
                yield packet


def fetch(srt_url, remote_file, local_file, flags=None):
    """
    fetch retrive a file over srt.

    srt_url   ex. srt://10.0.0.1:9000
    remote_file  ex.  /this/that/file.ts
    local_file    ex. /home/me/file.ts
    flags  a dict of socket flags you want to have set.
               in most situations this is not needed.
               ex. {SRTO_TRANSTYPE: SRT_LIVE,
                       SRTO_RCVSYN: 1, }
    """
    srtf = SRTfu(srt_url, flags)
    srtf.fetch(remote_file, local_file)
