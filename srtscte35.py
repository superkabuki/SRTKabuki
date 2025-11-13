#!/usr/bin/env python3

import sys
import time
from  srtkabuki import SRTKabuki
from threefive import Stream,Cue

PACKETSIZE=188
BUFFSIZE=1456
SYNC_BYTE=b'G'

def spinner(lc):
    """
    cli spinner to let you know things are running.
    """
    spin_map= {79:  ' |', 77: ' /',73: ' -',71: ' \\',}
   
    for k,v in spin_map.items():
        if lc % k == 0:
            print(v,'', end='\r')
            if lc %79 == 0:
                lc = 0

def sync_byte(stuff):
    """
    sync_byte check stuff for sync_byte
    """
    return stuff[0:1] == SYNC_BYTE


def parse_packet(packet,strm):
    """
    parse_packet check mpegts packet for scte35
    """
    if sync_byte(packet):
        if len(packet) == PACKETSIZE:
            cue=strm._parse(packet)
            if cue:
                Cue(packet).show()


def packetize(data):
    """
    packetize split data into mpegts packets
    """
    return [data[i : i + PACKETSIZE] for i in range(0, len(data), PACKETSIZE)]


def iter_packets(data,strm):
    """
    iter_packets iterate mpegts packets
    """
    _= [parse_packet(packet,strm) for packet in  packetize(data)]


def parse_mpegts(data, strm):
    """
    parse_mpegts split data into packets
    """
    if len(data) >=  PACKETSIZE:
        if sync_byte(data):
            iter_packets(data,strm)


def preflight():
    """
    preflight init SRTKabuki instance,
    a buffer, and a threefive.Stream instance
    """
    kabuki = SRTKabuki(sys.argv[1])
    kabuki.connect()
    buffsize=1456
    buffer = kabuki.mkbuff(BUFFSIZE)
    strm = Stream(tsdata=None)
    return kabuki, buffer, strm
    

if __name__ =='__main__':
    kabuki,buffer,strm = preflight()
    lc =0
    data=b''
    while True:
        st = kabuki.recvmsg(buffer)
        data=buffer.raw
        spinner(lc)
        lc +=1
        buffer = kabuki.mkbuff(BUFFSIZE)
        parse_mpegts(data, strm)

