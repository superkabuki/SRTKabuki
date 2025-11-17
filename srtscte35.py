#!/usr/bin/env python3

import sys
import time
from srtkabuki import SRTKabuki
from threefive import Stream, Cue


PACKETSIZE = 188
# set buffer to BUFFSIZE but send 1316 datagrams?
# That's how it reads to me, and it seems to work best.
BUFFSIZE = 1456 
SYNC_BYTE = b"G"
SPIN=True


def spinner(lc):
    """
    spinner show me things are working,
    it only spins when it's parsing data.
    """
    spins = ["|","\\",  "-", "/"]
    if SPIN:
        lc %= len(spins)
        print(spins[lc], file=sys.stderr, end="\r")
        lc +=1
    return lc


def has_sync_byte(stuff):
    """
    has_sync_byte check stuff for sync_byte
    """
    return stuff[0:1] == SYNC_BYTE


def at_least_a_packet(stuff):
    """
    at_least_a_packet  check if stuff  is at least PACKETSIZE
    """
    return len(stuff) >= PACKETSIZE
    

def parse_packet(packet, strm):
    """
    parse_packet check mpegts packet for scte35
    """
    if has_sync_byte(packet):
        if at_least_a_packet(packet):
            cue = strm._parse(packet)
            if cue:
                Cue(packet).show()


def packetize(datagram):
    """
    packetize split datagram into mpegts packets
    """
    return [datagram[i : i + PACKETSIZE] for i in range(0, len(datagram), PACKETSIZE)]


def parse_datagram(datagram, strm):
    """
    parse_datagram split datagram into mpegts packets
    """
    if at_least_a_packet(datagram):
        if has_sync_byte(datagram):
            _=[parse_packet(packet, strm) for packet  in packetize(datagram)]
                 

def preflight():
    """
    preflight init SRTKabuki instance,
    a buffer, and a threefive.Stream instance
    """
    kabuki = SRTKabuki(sys.argv[1])
    kabuki.connect()
    buffer = kabuki.mkbuff(BUFFSIZE)
    strm = Stream(tsdata=None)
    return kabuki, buffer, strm


if __name__ == "__main__":
    kabuki, buffer, strm = preflight()
    lc = 0
    datagram = b""
    while True:
        st = kabuki.recvmsg(buffer)
        datagram = buffer.raw
        lc = spinner(lc)
        buffer = kabuki.mkbuff(BUFFSIZE)
        parse_datagram(datagram, strm)




















