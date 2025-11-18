# `S`ecure `R`eliable `T`ransport `Kabuki`
### Call [libsrt](https://github.com/Haivision/srt) C functions from python.

### My goal here is to be able to use the SRT protocol in python 
and to do so with just a few lines of code.
<BR> 
___

## When is the release coming?

I'm fixing to get ready to start a release.
__probably by Thanksgiving I will make a testing release__.

___

## Supported Operating Systems

* Tested on __OpenBSD and Debian Sid__. 
* __If you can install libsrt__ in your environment, __SRTKabuki should work just fine.__
* __I don't know Windows well enough to support it__, but I will accept Windows specific patches if needed.

___

### SRTKabuki is classy.
* SRTKabuki is a python class that implements SRT. <BR>
* No matter what you're doing, you start with
```py3
from srtkabuki import SRTKabuki

srtk = SRTKabuki(srt_url) # srt://1.2.3.4:9000

```
* method names map to srt_function names _(ex. SRTKabuki.connect is libsrt.srt_connect)_

___
### SRTKabuki is fast.
* since it calls libsrt C functions, SRTKabuki runs at C speed.
___ 
###  Get invovled or go away.
__If you use open source, contribute to open source.__<BR>

If you are interested in using SRT from python, come work on it with me..<BR>
You don't need to be a master of python, there's stuff to do besides just writing code.<BR>

___

### NEWS
* 11/17/2025 : __Of course SRTKabuki runs on OpenBSD__ 
* 11/16/2025 : libsrt now builds correctly and  builds the srt apps correctly with clang++ on OpenBSD
* 11/14/2025 : added methods __SRTKabuki.livecc()__ and __SRTKabuki.filecc()__ to set __congestion control algorithm.__
* 11/12/2025 : __Parsing SCTE-35 from SRT__ is now working. 
* 11/08/2025 : __Boom goes the dynamite, reading srt output from srt-live-transmit now works.__
* 11/05/2025 : It's porting pretty smooth, __cyclomatic complexity__ so far is __1.09__, that is sweet..
* 11/04/2025 : started on epoll stuff. it's really started coming together, a couple more weeks to a release I think.
* 11/01/2025 :  rewrote examples test-c-server.c and test-c-client.c, using SRTKabuki and they both work. 
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting SRTO_TRANSTYPE and SRT_SOCKOPT correctly ,but I figured it out today.Super jazzed
___
### Install 
##### (This is just for pre-release testing)

* __step 1__ ( if you have libsrt already installed, you can skip this step )

```sh
git clone https://github.com/Haivision/srt
cd srt
cmake build .
make all   # libsrt.so will be in this directory
make install # this will install to /usr/local/lib, make sure the path is in your LD_LIBRARY_PATH, or however you find libs.

```
* __step 2__
```sh
git clone https://github.com/superkabuki/SRTKabuki  

```
* I'll do a pip package soon.


# Examples
* The smoketest from the libsrt docs.
* Install libsrt https://github.com/Haivision/srt
* create the file livekabuki.py
```py3
#!/usr/bin/env python3

import sys
from  srtkabuki import SRTKabuki


kabuki = SRTKabuki(sys.argv[1]) # srt://127.0.0.1:9000
kabuki.connect()
buffsize=1316
buffer = kabuki.mkbuff(buffsize)
while True:
    st = kabuki.recvmsg(buffer)
    sys.stdout.buffer.write(buffer.raw)
```

* In a terminal window run

```js
ffmpeg -f lavfi -re -i smptebars=duration=300:size=1280x720:rate=30\
-f lavfi -re -i sine=frequency=1000:duration=60:sample_rate=44100\
-pix_fmt yuv420p -c:v libx264 -b:v 1000k -g 30 -keyint_min 120\
-profile:v baseline -preset veryfast -f mpegts "udp://127.0.0.1:1234?pkt_size=1316"
```

* In another terminal run

```awk
srt-live-transmit udp://127.0.0.1:1234 srt://:4201 
```
* In yet another window run

```sed
python3 livekabuki.py srt://127.0.0.1:4201 | ffplay -
```
___
# Parse SCTE-35 from SRT streams with SRTKabuki

1) Do install from above
2) pip install threefive
3) read srt stream with srtscte35.py
```py3

python3 srtscte35.py srt://127.0.0.1:4201
```

5) output
```js
a@fu:~/srt$ python3 srtscte35.py srt://127.0.0.1:4201
127.0.0.1 4201
startup: ✓
ipv4int: ✓
create_socket: ✓
connect: ✓
{\ 
    "info_section": {
        "table_id": "0xfc",
        "section_syntax_indicator": false,
        "private": false,
        "sap_type": "0x03",
        "sap_details": "No Sap Type",
        "section_length": 67,
        "protocol_version": 0,
        "encrypted_packet": false,
        "encryption_algorithm": 0,
        "pts_adjustment": 2.3,
        "cw_index": "0x00",
        "tier": "0x0fff",
        "splice_command_length": 20,
        "splice_command_type": 5,
        "descriptor_loop_length": 30,
        "crc": "0x37b199ef"
    },
    "command": {
        "command_length": 20,
        "command_type": 5,
        "name": "Splice Insert",
        "time_specified_flag": true,
        "pts_time": 72825.523933,
        "break_auto_return": true,
        "break_duration": 119.986533,
        "splice_event_id": 1,
        "splice_event_cancel_indicator": false,
        "out_of_network_indicator": true,
        "program_splice_flag": true,
        "duration_flag": true,
        "splice_immediate_flag": false,
        "event_id_compliance_flag": true,
        "unique_program_id": 39321,
        "avail_num": 1,
        "avails_expected": 1
    },
    "descriptors": [
             {
            "tag": 2,
            "identifier": "CUEI",
            "name": "Segmentation Descriptor",
            "descriptor_length": 28,
            "segmentation_event_cancel_indicator": false,
            "segmentation_event_id": "0x00",
            "segmentation_event_id_compliance_indicator": true,
            "program_segmentation_flag": true,
            "segmentation_duration_flag": true,
            "delivery_not_restricted_flag": false,
            "web_delivery_allowed_flag": false,
            "no_regional_blackout_flag": false,
            "archive_allowed_flag": false,
            "device_restrictions": "Restrict Group 0",
            "segmentation_duration": 120.0,
            "segmentation_message": "Provider Placement Opportunity Start",
            "segmentation_type_id": 52,
            "segmentation_upid_length": 8,
            "segmentation_upid_type": 1,
            "segmentation_upid_type_name": "Type 0x01 is deprecated, use MPU type 0x0C",
            "segmentation_upid": "10100000",
            "segment_num": 0,
            "segments_expected": 0
        }
    ]
```

look in the examples directory to see the original c/c++ examples and the rewrites using SRTKabuki.
___


# Here's where I'm at so far.

```py3
Help on class SRTKabuki in module srtkabuki:
class SRTKabuki(builtins.object)
 |  SRTKabuki(srturl)
 |  
 |  SRTKabuki Pythonic Secure Reliable Transport
 |  
 |  Methods defined here:
 |  
 |  __init__(self, srturl)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  accept(self)
 |      accept srt_accept
 |  
 |  bind(self)
 |      bind  srt_bind
 |  
 |  chk_sock(self, sock=None)
 |      chk_sock if we don't have a sock, use self.sock
 |  
 |  cleanup(self)
 |      cleanup srt_cleanup
 |  
 |  close(self, sock=None)
 |      close srt_close
 |  
 |  congestion_control(self, algo)
 |      congestion_control set the congestion control
 |      algorithm. can also be set with livecc() and filecc()
 |      methods.
 |  
 |  connect(self)
 |      connect srt_connect
 |  
 |  create_socket(self)
 |      create_socket srt_create_socket
 |  
 |  epoll_add_usock(self, events)
 |      epoll_add_usock srt_epoll_add_usock
 |  
 |  epoll_create(self)
 |      epoll_create srt_epoll_create
 |  
 |  epoll_wait(self, readfds, writefds, ms_timeout, lrfds, lwfds)
 |      epoll_wait srt_epoll_wait
 |  
 |  fetch(self, remote_file, local_file)
 |      fetch fetch remote_file fron host on port
 |      and save it as local_file
 |  
 |  filecc(self)
 |      filecc set congestion control to file
 |  
 |  getlasterror(self)
 |      getlasterror srt_getlasterror_str
 |  
 |  getsockstate(self, sock=None)
 |      getsockstate srt_getsockstate
 |  
 |  ipv4int(self, addr)
 |      take a ipv4 string addr and make it an int
 |  
 |  listen(self)
 |      listen srt_listen
 |  
 |  livecc(self)
 |      livecc set congestion control to live
 |  
 |  load_libc(self)
 |      load_libc load getaddrinfo and freeaddrinfo from libc.so
 |  
 |  load_srt(self)
 |      load_srt load everything from libsrt.so
 |  
 |  mk_sockaddr_ptr(self, addr, port)
 |      mk_sockaddr_sa make a c compatible (struct sockaddr*)&sa
 |  
 |  mkbuff(self, buffsize, data=b'')
 |      mkbuff make a c  buffer
 |      to read into when receiving data.
 |  
 |  mkmsg(self, msg)
 |      mkmsg convert python byte string
 |      to a C string buffer when sending data
 |  
 |  new_val(self, val)
 |      new_val convert val into a ctypes type
 |  
 |  recv(self, buffer, sock=None)
 |      recv srt_recv
 |  
 |  recvfile(self, local_file, sock=None)
 |      recvfile srt_recvfile
 |  
 |  recvmsg(self, buffer, sock=None)
 |      recvmsg srt_recvmsg
 |  
 |  remote_file_size(self)
 |      read the remote file size message
 |  
 |  request_file(self, remote_file)
 |      request_file request a file from a server
 |  
 |  send(self, msg, sock=None)
 |      send srt_send
 |  
 |  sendfile(self, filename, sock=None)
 |        sendfile srt_sendfile
 |  
 |  sendmsg2(self, msg, sock=None)
 |      sendmsg2 srt_sendmsg2
 |  
 |  setsockflag(self, flag, val)
 |      setsockflag  srt_setsockflag
 |  
 |  startup(self)
 |      startup  srt_startup()
 |  
 |  ----------------------------------------------------------------------
 |  Static methods defined here:
 |  
 |  split_url(url)
 |      split_url, split srt url into addr,port, path and args
 |  
 |  ----------------------------------------------------------------------

  
```
