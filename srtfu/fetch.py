"""
fetch.py
the fetch function for retriving files over srt
"""

from .srtfu import SRTfu


def set_flags(srtf, flags):
    """
    set_flags set flags on an SRTfu instance

    srtf SRTfu instance
    flags  a dict of socket flags you want to have set.
               ex. {SRTO_TRANSTYPE: SRT_LIVE,
                       SRTO_RCVSYN: 1, }

    """
    for k,v in flags:
        srtf.setsockflag(k,v)    



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
    if flags:
        set_flags(srtf, flags)
    srtf.fetch(remote_file, local_file)
