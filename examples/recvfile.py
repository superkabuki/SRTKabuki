 #!/usr/bin/env python3
'''
This is the SRTKabuki version of examples/recvfile.cpp in libsrt
https://github.com/Haivision/srt/blob/master/examples/recvfile.cpp

'''

import sys
from srtkabuki import SRTKabuki

addr = sys.argv[1]
port = sys.argv[2]
remote_file = sys.argv[3]
local_file = sys.argv[4]

srtk=SRTKabuki(addr=addr,port=port)
srtk.fetch(remote_file,local_file)
