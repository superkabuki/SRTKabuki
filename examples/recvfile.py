#!/usr/bin/env python3
"""
This is the SRTfu version of examples/recvfile.cpp in libsrt
https://github.com/Haivision/srt/blob/master/examples/recvfile.cpp

"""

import sys
from srtfu import fetch

srt_url = sys.argv[1]  # srt://example.com:9000
remote_file = sys.argv[2]
local_file = sys.argv[3]

fetch(srt_url , remote_file, local_file)
