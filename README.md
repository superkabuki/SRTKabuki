# `S`ecure `R`eliable `T`ransport `Kabuki`
### Call [libsrt](https://github.com/Haivision/srt) C functions from python.

___

### NEWS
* 11/25/2025 : __Release v0.0.1 is now available via pip__ _(..and the crowd goes wild!)_
* 11/25/2025 : added __datagramer__, pythonic fast __datagam generator__ live srt stream parsing. 
* 11/20/2025 : __SRTKabuki__ __is working__.
* 11/19/2025 : cyclomatic complexity __A (1.2790697674418605)__
* 11/18/2025 : rewrote examples __sendfile.cpp__ and __recvfile.cpp__ with __SRTKabuki__, both are working.
* 11/17/2025 : __Of course SRTKabuki runs on OpenBSD__ 
* 11/16/2025 : libsrt now builds correctly and  builds the srt apps correctly with clang++ on OpenBSD
* 11/14/2025 : added methods __SRTKabuki.livecc()__ and __SRTKabuki.filecc()__ to set __congestion control algorithm.__
* 11/12/2025 : __Parsing SCTE-35 from SRT__ is now working. 
* 11/08/2025 : __Boom goes the dynamite, reading srt output from srt-live-transmit now works.__
* 11/05/2025 : It's porting pretty smooth, __cyclomatic complexity__ so far is __1.09__, that is sweet..
* 11/04/2025 : started on __epoll__ stuff. it's really started coming together, a couple more weeks to a release I think.
* 11/01/2025 :  rewrote examples __test-c-server.c__ and __test-c-client.c__, using SRTKabuki and they both work. 
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting __SRTO_TRANSTYPE__ and __SRT_SOCKOPT__ correctly ,but I figured it out today.Super jazzed
___

### My goal here is to be able to use the SRT protocol in python 
and to do so with just a few lines of code.
<BR> 
___

## When is the release coming?

<s>I'm fixing to get ready to start a release.
__probably by Thanksgiving I will make a testing release__. </s>

__v0.0.1 is out__ _(and a little buggy)_. I will sos a new build with fixes this weekend.

___

## Supported Operating Systems
* __POSIX__ systems ( UNIX, Linux)
* Tested on __OpenBSD and Debian Sid__. 
* __If you can install libsrt__ in your environment, __SRTKabuki should work just fine.__
* __I don't know Windows well enough to support it__, but I will accept Windows specific patches if needed.

___

### SRTKabuki is classy.
* SRTKabuki is a python class that implements SRT. <BR>
* Start with
```py3
from srtkabuki import SRTKabuki

srtk = SRTKabuki(srt_url) # srt://1.2.3.4:9000

```
* method names map to srt_function names _(ex. SRTKabuki.connect is libsrt.srt_connect)_

### Well most of the time it's classy
* For parsing raw live srt streams you can use the datagramer generator function

```py3
from srtkabuki import datagramer  

srt_url = 'srt://10.10.11.13:9000'

for datagram in datagramer(srt_url):
    your_datagram_parser(datagram)
```

### SRTKabuki is fast.
* since it calls libsrt C functions, SRTKabuki runs at C speed.
___ 
###  Get invovled or go away.
__If you use open source, contribute to open source.__<BR>

If you are interested in using SRT from python, come work on it with me..<BR>
You don't need to be a master of python, there's stuff to do besides just writing code.<BR>

___

### Install 
##### Install libsrt

*if you have libsrt already installed, you can skip this step

* Check if your os has a libsrt package and install it. SRTKabuki is built with libsrt v1.5.5.

* or run the the install-libsrt.sh script in this repo.

##### Install SRTKabuki
```sh
python3 -mpip install srtkabuki --break-system-packages
```
___

# Examples

##### The smoketest from the libsrt docs.

* create the file livekabuki.py
```py3
#!/usr/bin/env python3

import sys
from  srtkabuki import SRTKabuki


kabuki = SRTKabuki(sys.argv[1]) # srt://127.0.0.1:9000
kabuki.connect()
buffsize=1456
buffer = kabuki.mkbuff(buffsize)
while True:
    kabuki.recvmsg(buffer)
    sys.stdout.buffer.write(buffer.raw)
    buffer = kabuki.mkbuff(buffsize)
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

##### parsing SCTE-35 from an srt stream with threefive

* install [threefive](https://github.com/superkabuki/SCTE35-Kabuki)
  ```py3
  python3 -mpip install threefive --break-system-packages
  ```
* datagramer is great when you need to add srt support to a parser like threefive.

* threefive doesn't directly support srt, so datagramer reads the srt stream and passes data to threefive.


```py3
from srtkabuki import datagramer
from threefive import Stream 

PACKETSIZE=188

def parseSCTE35(strm, datagram):
"""
parseSCTE35 split datagram into packets and
pass to a threefive.Stream instance for parsing.
"""
_= [strm._parse(packet) for packet in
    [datagram[i : i + PACKETSIZE]
     for i in range(0, len(datagram), PACKETSIZE)]]


if __name__=='__main__':
    srt_url = 'srt://10.10.11.13:9000'
    strm = Stream(tsdata=None) 
    for datagram in datagramer(srt_url):
        parseSCTE35(datagram, strm)
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

___


# Here's where I'm at so far.

## SRTKabuki

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
 |     new_val convert val into a ctypes type
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
 |  
 |  request_file(self, remote_file)
 |      request_file request a file from a server
 |  
 |  send(self, msg, sock=None)
 |      send srt_send
 |  
 |  sendfile(self, filename, sock=None)
 |      sendfile srt_sendfile
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

## sockopts
```py3
Help on module sockopts:

NAME
    sockopts - sockopts.py

DESCRIPTION
    these are the SRT socket options.
    libsrt has them in an enum,
    but I like being able to do
    
    from sockopts import  SRTO_RCVSYN
    
    it just seems more pythonic.

DATA
SRTO_MSS = 0  # the Maximum Transfer Unit
SRTO_SNDSYN = 1  # if sending is blocking
SRTO_RCVSYN = 2  # if receiving is blocking
SRTO_ISN = 3  # Initial Sequence Number
SRTO_FC = 4  # Flight flag size (window size)
SRTO_SNDBUF = 5  # maximum buffer in sending queue
SRTO_RCVBUF = 6  # UDT receiving buffer size
SRTO_LINGER = 7  # waiting for unsent data when closing
SRTO_UDP_SNDBUF = 8  # UDP sending buffer size
SRTO_UDP_RCVBUF = 9  # UDP receiving buffer size
# (some space left)
SRTO_RENDEZVOUS = 12  # rendezvous connection mode
SRTO_SNDTIMEO = 13  # send() timeout
SRTO_RCVTIMEO = 14  # recv() timeout
SRTO_REUSEADDR = 15  # reuse an existing port or create a new one
SRTO_MAXBW = 16  # maximum bandwidth (bytes per second) that the connection can use
SRTO_STATE = 17  # current socket state see SRT_SOCKSTATUS read only
SRTO_EVENT = 18  # current available events associated with the socket
SRTO_SNDDATA = 19  # size of data in the sending buffer
SRTO_RCVDATA = 20  # size of data available for recv
SRTO_SENDER = 21  # Sender mode
SRTO_TSBPDMODE = 22  # Enable/Disable TsbPd. Enable -> Tx set origin timestamp Rx deliver packet at origin time + delay
SRTO_LATENCY = 23  # NOT RECOMMENDED. SET: to both SRTO_RCVLATENCY and SRTO_PEERLATENCY. GET: same as SRTO_RCVLATENCY.
SRTO_INPUTBW = 24  # Estimated input stream rate.
SRTO_OHEADBW = 25  # MaxBW ceiling based on % over input stream rate. Applies when UDT_MAXBW=0 (auto).
SRTO_PASSPHRASE = 26  # Crypto PBKDF2 Passphrase (must be 10..79 characters or empty to disable encryption)
SRTO_PBKEYLEN = 27  # Crypto key len in bytes {162432} Default: 16 (AES-128)
SRTO_KMSTATE = 28  # Key Material exchange status (UDT_SRTKmState)
SRTO_IPTTL = 29  # IP Time To Live (passthru for system sockopt IPPROTO_IP/IP_TTL)
SRTO_IPTOS = 30  # IP Type of Service (passthru for system sockopt IPPROTO_IP/IP_TOS)
SRTO_TLPKTDROP = 31  # Enable receiver pkt drop
SRTO_SNDDROPDELAY = 32  # Extra delay towards latency for sender TLPKTDROP decision (-1 to off)
SRTO_NAKREPORT = 33  # Enable receiver to send periodic NAK reports
SRTO_VERSION = 34  # Local SRT Version
SRTO_PEERVERSION = 35  # Peer SRT Version (from SRT Handshake)
SRTO_CONNTIMEO = 36  # Connect timeout in msec. Caller default: 3000 rendezvous (x 10)
SRTO_DRIFTTRACER = 37  # Enable or disable drift tracer
SRTO_MININPUTBW = 38  # Minimum estimate of input stream rate.
# (some space left)
SRTO_SNDKMSTATE = 40  # (GET) the current state of the encryption at the peer side
SRTO_RCVKMSTATE = 41  # (GET) the current state of the encryption at the agent side
SRTO_LOSSMAXTTL = 42  # Maximum possible packet reorder tolerance (number of packets to receive after loss to send lossreport)
SRTO_RCVLATENCY = 43  # TsbPd receiver delay (mSec) to absorb burst of missed packet retransmission
SRTO_PEERLATENCY = 44  # Minimum value of the TsbPd receiver delay (mSec) for the opposite side (peer)
SRTO_MINVERSION = 45  # Minimum SRT version needed for the peer (peers with less version will get connection reject)
SRTO_STREAMID = 46  # A string set to a socket and passed to the listener's accepted socket
SRTO_CONGESTION = 47  # Congestion controller type selection
SRTO_MESSAGEAPI = 48  # In File mode use message API (portions of data with boundaries)
SRTO_PAYLOADSIZE = 49  # Maximum payload size sent in one UDP packet (0 if unlimited)
SRTO_TRANSTYPE = 50  # Transmission type (set of options required for given transmission type)
SRTO_KMREFRESHRATE = 51  # After sending how many packets the encryption key should be flipped to the new key
SRTO_KMPREANNOUNCE = 52  # How many packets before key flip the new key is annnounced and after key flip the old one decommissioned
SRTO_ENFORCEDENCRYPTION = 53  # Connection to be rejected or quickly broken when one side encryption set or bad password
SRTO_IPV6ONLY = 54  # IPV6_V6ONLY mode
SRTO_PEERIDLETIMEO = 55  # Peer-idle timeout (max time of silence heard from peer) in [ms]
SRTO_BINDTODEVICE = 56  # Forward the SOL_SOCKET/SO_BINDTODEVICE option on socket (pass packets only from that device)
SRTO_GROUPCONNECT = 57  # Set on a listener to allow group connection (ENABLE_BONDING)
SRTO_GROUPMINSTABLETIMEO = 58  # Minimum Link Stability timeout (backup mode) in milliseconds (ENABLE_BONDING)
SRTO_GROUPTYPE = 59  # Group type to which an accepted socket is about to be added available in the handshake (ENABLE_BONDING)
SRTO_PACKETFILTER = 60  # Add and configure a packet filter
SRTO_RETRANSMITALGO = 61  # An option to select packet retransmission algorithm
SRTO_CRYPTOMODE = 62  # Encryption cipher mode (AES-CTR AES-GCM ...).
SRTO_MAXREXMITBW = 63  # Maximum bandwidth limit for retransmision (Bytes/s)
```
## static
```py3

Help on module static:

NAME
    static

DESCRIPTION
    static.py
    srt constants

DATA
    AF_INET = <AddressFamily.AF_INET: 2>
    AI_PASSIVE = <AddressInfo.AI_PASSIVE: 1>
    SOCK_DGRAM = <SocketKind.SOCK_DGRAM: 2>
    SRTS_BROKEN = 6
    SRTS_CLOSED = 8
    SRTS_CLOSING = 7
    SRTS_CONNECTED = 5
    SRTS_CONNECTING = 4
    SRTS_INIT = 1
    SRTS_LISTENING = 3
    SRTS_NONEXIST = 9
    SRTS_OPENED = 2
    SRT_DEFAULT_RECVFILE_BLOCK = 7200
    SRT_ERROR = -1
    SRT_FILE = 1
    SRT_INVALID = 2
    SRT_LIVE = 0
    SRT_LIVE_DEF_LATENCY_MS = 120
    SRT_LIVE_DEF_PLSIZE = 1316
    SRT_LIVE_MAX_PLSIZE = 1456

```

