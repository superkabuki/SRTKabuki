"""
funcs.py

Home of the fetch and datagramer functions.

"""
import sys
import time
from .srtfu import SRTfu
from . import SRTO_TRANSTYPE, SRTO_RCVSYN, SRTO_RCVBUF, SRT_LIVE, SRT_FILE


PACKETSIZE = 188
BUFFSIZE = 1456


def _setflags(srtf, flags):
    """
    _setflags set flags on an SRTfu instance

    srtf SRTfu instance
    flags  a dict of socket flags you want to have set.
               ex. {SRTO_TRANSTYPE: SRT_LIVE,
                       SRTO_RCVSYN: 1, }
    """
    for k,v in flags.items():
        srtf.setsockflag(k,v)


def _preflight(srt_url, flags=None):
    """
    preflight init SRTfu instance,
    and set sock flags as desired.
    """
    srtf= SRTfu(srt_url)
    if flags:
        _setflags(srtf, flags)
    srtf.connect()
    return srtf


def datagramer(srt_url,flags=None):
    """
    datagramer datagram generator
    take a live srt_url
    and return datagrams
    """
    preflags ={SRTO_TRANSTYPE: SRT_LIVE,
                       SRTO_RCVSYN: 1,
                       SRTO_RCVBUF: 32768,}
    if flags:
        preflags.update(flags)
    srtf = _preflight(srt_url,preflags)
    while True:
        buffer = srtf.mkbuff(BUFFSIZE)
        st = srtf.recv(buffer)
        datagram = buffer.raw
        yield datagram



def fetch(srt_url, remote_file,local_file, flags=None):
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

        
    srtf = SRTfu(srt_url)
    srtf.fetch(remote_file, local_file)
