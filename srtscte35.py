#!/usr/bin/env python3

import sys
from srtkabuki import SRTKabuki
from threefive import Stream, Cue


PACKETSIZE = 188
BUFFSIZE = 1316
SYNC_BYTE = b"G"


def spinner(lc):
    """
    cli spinner to let you know things are running.
    """
    spins = ["\\", "-", "/", "|"]
    lc %= len(spins)
    print(spins[lc], file=sys.stderr, end="\r")


def sync_byte(data):
    """
    sync_byte check stuff for sync_byte
    """
    return data[0:1] == SYNC_BYTE


def parse_packet(packet, strm):
    """
    parse_packet check mpegts packet for scte35
    """
    if sync_byte(packet):
        if len(packet) == PACKETSIZE:
            cue = strm._parse(packet)
            if cue:
                Cue(packet).show()


def packetize(data):
    """
    packetize split data into mpegts packets
    """
    return [data[i : i + PACKETSIZE] for i in range(0, len(data), PACKETSIZE)]


def parse_mpegts(data, strm):
    """
    parse_mpegts split data into packets
    """
    if len(data) >= PACKETSIZE:
        if sync_byte(data):
            _=[parse_packet(packet, strm) for packet  in packetize(data)]


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
    data = b""
    while True:
        st = kabuki.recvmsg(buffer)
        data = buffer.raw
        spinner(lc)
        lc += 1
        buffer = kabuki.mkbuff(BUFFSIZE)
        parse_mpegts(data, strm)
