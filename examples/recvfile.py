#!/usr/bin/env python3
"""
This is the SRTKabuki version of examples/recvfile.cpp in libsrt
https://github.com/Haivision/srt/blob/master/examples/recvfile.cpp

"""

import sys
from srtkabuki import SRTKabuki

srt_url = sys.argv[1]  # srt://example.com:9000
remote_file = sys.argv[2]
local_file = sys.argv[3]

srtk = SRTKabuki(srt_url)
srtk.fetch(remote_file, local_file)
