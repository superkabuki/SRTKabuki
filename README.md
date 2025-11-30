# SRTfu
# Pythonic Secure Reliable Transport

### Call [libsrt](https://github.com/Haivision/srt) C functions from python.

___

### NEWS
* 11/28/2025 : __Fixed datagramer__, tested for 8 hours straight parsing SCTE35, __513 cues out of 513 cues parssed correctly__.
* 11/25/2025 : __Release v0.0.1 is now available via pip__ _(..and the crowd goes wild!)_
* 11/25/2025 : added __datagramer__, pythonic fast __datagam generator__ live srt stream parsing. 
* 11/20/2025 : __SRTfu__ __is working__.
* 11/19/2025 : cyclomatic complexity __A (1.2790697674418605)__
* 11/18/2025 : rewrote examples __sendfile.cpp__ and __recvfile.cpp__ with __SRTfu__, both are working.
* 11/17/2025 : __Of course SRTfu runs on OpenBSD__ 
* 11/16/2025 : libsrt now builds correctly and  builds the srt apps correctly with clang++ on OpenBSD
* 11/14/2025 : added methods __SRTfu.livecc()__ and __SRTfu.filecc()__ to set __congestion control algorithm.__
* 11/12/2025 : __Parsing SCTE-35 from SRT__ is now working. 
* 11/08/2025 : __Boom goes the dynamite, reading srt output from srt-live-transmit now works.__
* 11/05/2025 : It's porting pretty smooth, __cyclomatic complexity__ so far is __1.09__, that is sweet..
* 11/04/2025 : started on __epoll__ stuff. it's really started coming together, a couple more weeks to a release I think.
* 11/01/2025 :  rewrote examples __test-c-server.c__ and __test-c-client.c__, using SRTfu and they both work. 
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting __SRTO_TRANSTYPE__ and __SRT_SOCKOPT__ correctly ,but I figured it out today.Super jazzed
___

### My goal here is to be able to use the SRT protocol in python 
and to do so with just a few lines of code.
<BR> 
___

## When is the release coming?

I'm fixing to get ready to start a release.
__v0.0.3 being released today__. 

___

## Supported Operating Systems
* __POSIX__ systems ( UNIX, Linux)
* Tested on __OpenBSD and Debian Sid__. 
* __If you can install libsrt__ in your environment, __SRTfu should work just fine.__
* __I don't know Windows well enough to support it__, but I will accept Windows specific patches if needed.

___

### SRTfu is classy.
* SRTfu is a python class that implements SRT. <BR>
* Start with
```py3
from srtfu import SRTfu

srtk = SRTfu(srt_url) # srt://1.2.3.4:9000

```
* method names map to srt_function names _(ex. SRTfu.connect is libsrt.srt_connect)_

### Well most of the time it's classy
* For parsing raw live srt streams you can use the datagramer generator function

```py3
from srtfu import datagramer  

srt_url = 'srt://10.10.11.13:9000'

for datagram in datagramer(srt_url):
    your_datagram_parser(datagram)
```

### SRTfu is fast.
* since it calls libsrt C functions, SRTfu runs at C speed.
___ 
###  Get invovled or go away.
__If you use open source, contribute to open source.__<BR>

If you are interested in using SRT from python, come work on it with me..<BR>
You don't need to be a master of python, there's stuff to do besides just writing code.<BR>

___

### Install 
##### Install libsrt

*if you have libsrt already installed, you can skip this step

* Check if your os has a libsrt package and install it. SRTfu is built with libsrt v1.5.5.

* or run the the install-libsrt.sh script in this repo.

### Install SRTfu
```sh
python3 -mpip install srtfu --break-system-packages
```
___

# Examples

### The smoketest from the libsrt docs.

* create the file livekabuki.py
```py3
#!/usr/bin/env python3

import sys
from  srtfu import SRTfu


kabuki = SRTfu(sys.argv[1]) # srt://127.0.0.1:9000
kabuki.connect()
buffsize=1456
while True:
    buffer = kabuki.mkbuff(buffsize)
    kabuki.recvmsg(buffer)
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

### parsing SCTE-35 from an srt stream with threefive

* install [threefive](https://github.com/superkabuki/SCTE35-Kabuki)
  ```py3
  python3 -mpip install threefive --break-system-packages
  ```
* datagramer is great when you need to add srt support to a parser like threefive.

* threefive doesn't directly support srt, so datagramer reads the srt stream and passes data to threefive.

* Run [srtscte35.py](examples/srtscte35.py)  in examples directory.
___

### Using the SRTfu lib
* If you just want to do a file transfer with SRTfu you can use the fetch method

```py3
#!/usr/bin/env python3

import sys
from srtfu import SRTfu

srt_url = sys.argv[1]  # srt://example.com:9000
remote_file = sys.argv[2]
local_file = sys.argv[3]

srtk = SRTfu(srt_url)
srtk.fetch(remote_file, local_file)
```
* if you just want the raw datagrams off a live feed use the datagramer generator function
* datagramer takes a srt_url as an arg, returns datagrams as bytes, payload size is 1316. 

```py3
import sys
from srtfu import datagramer
srt_url = sys.argv[1]  # srt://example.com:9000

for datagram in datagramer:
    your_parsing_function(datagram)
```
### Going low level
* Most of libsrt is available in SRTfu, the ctypes conversions are handled for you.
* If you've used sockets, this will all seem very similar.
* One note, the socket is an optional arg in methods, it only needs to be used when a server accepts a socket connection. 
* init SRTfu instance, just provide a srt_url
* a socket is created for you, but not connected.
* the srt_url sets host and port to bind for servers (0.0.0.0 works), and host and port to connect for clients 
```py3
from srtfu import SRTfu

srtk = SRTKabki(srt_url)
```
* next you can set sock flags
* All constants are in srtfu.srt_h
```py3
    from srtfu.srt_h import SRTO_TRANSTYPE,SRT_LIVE,SRTO_RCVSYN,SRTO_RCVBUF

    kabuki.setsockflag(SRTO_TRANSTYPE,SRT_LIVE)
    kabuki.setsockflag(SRTO_RCVSYN,1)
    kabuki.setsockflag(SRTO_RCVBUF,32768)

```
* for clients call connect
```py3
kabuki.connect()
```
*  for servers call bind and listen
```py3
  kabuki.bind()
  kabuki.listen()
```
* to accept a connection on a server
```py3
    fhandle = kabuki.accept() 
```
* to receive from a client
* Note the socket is always the last arg
```py3
 smallbuff = kabuki.mkbuff(1456)
 kabuki.recv(smallbuff, fhandle)
```
* If you need a buffer to receive into

```py3
  smallbuff = kabuki.mkbuff(1456)
```
* if you need to send data in a buffer

```py3
message = 'message can be strings, bytes, or ints'
new_message= kabuki.mkmsg(message)
```

* to receive from a client
* Note the socket is always the last arg

```py3
 smallbuff = kabuki.mkbuff(1456)
 kabuki.recv(smallbuff, fhandle)
```

# Here's where I'm at so far.

## SRTfu

```py3
Help on class SRTfu in module srtfu:

class SRTfu(builtins.object)
 |  SRTfu(srturl)
 |  
 |  SRTfu Pythonic Secure Reliable Transport
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

## srt_h

```py3

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

