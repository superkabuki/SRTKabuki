#!/usr/bin/env python3
"""
This is the SRTfu version of examples/recvfile.cpp in libsrt
https://github.com/Haivision/srt/blob/master/examples/recvfile.cpp

"""

import sys
from srtfu import fetch, SRTO_TRANSTYPE, SRT_FILE


if __name__ == '__main__':
    srt_url = sys.argv[1]  # srt://example.com:9000
    remote_file = sys.argv[2]
    local_file = sys.argv[3]

    flags={SRTO_TRANSTYPE: SRT_FILE,}
    fetch(srt_url , remote_file, local_file, flags)
