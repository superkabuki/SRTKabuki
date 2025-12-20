## Heads up:  __s/SRTKabuki/SRTfu/g__ 


# SRTfu
# Pythonic Secure Reliable Transport

### Call [libsrt](https://github.com/Haivision/srt) C functions from python.

___

### NEWS
* 12/19.2025 : __fixed__ packet loss in __packetizer__ and __SRTfu.read()__
* 12/17/2025 : __libsrt is now automatically built for SRTfu__ This is pretty slick. __Available in v0.0.9__ 
* 12/12/2025 : __I am back peddling on my decision to unroll the enums from srt.h__. I think the enums are the better way, __enums will be back in the next release__ instead of all the individual constants.
* 12/11/2025 : __Working on throttling__ so SRTfu can intake at any speed and output in realtime, __like ffmpeg`s '-re'__.
* 12/10/2025 : [threefive, __God`s favorite SCTE35 parser__](https://github.com/superkabuki/SCTE35), now uses __SRTfu__ to handle SRT. 
* 12/08/2025 :  __Release v0.0.7__ aka _'I got your packet hanging right here!'_
* 12/07/2025 : the rise of __packetizer__
* 12/01/2025 : __Release v0.0.5__ aka _'everything is working?'_
* 11/29/2025 : __Renaming project to SRTfu__, SRTKabuki does not work well with search engines.
* 11/29/2025 : Released __v0.0.3__


# Docs

* [Install](#install)
* [Examples](https://github.com/superkabuki/SRTfu/tree/main/examples) several of the libsrt rewritten with srtfu, and a SCTE35 parsing example.
* [Usage](#usage)
  * [packetizer](#packetizer) - mpegts packets from SRT live stream 
  * [fetch](#fetch) - file transfer
  * [datagramer](#datagramer) - parsing video streams
  * [smoketest](#smoketest) - the smoketest from libsrt in srtfu.
  * [SCTE35](#scte35) - parse scte35 from srt
  * [low level](#low-level) - using the SRTfu class.
  * [SRTfu](#srtfu) -all the SRTfu methods
  * [socket flags](#socket-flags) - SRT uses a lot of socket flags.
    
___

### Install 
##### Install libsrt
* __Requires clang or gcc, cmake, git,gmake or make, and openssl__
* The first time you use SRTfu libsrt will be built and installed automatically into the SRTfu site-packages directory.
* the libsrt in the SRTfu directory will only be used by SRTfu. 

### Install SRTfu
```sh
python3 -mpip install srtfu --break-system-packages
```
___



# Usage
#### srtfu handles the ctype conversion and pointers. 

* srtfu is meant be easy to use.
* use __packetizer__ to receive SRT stream as mpegts packets.
* Use [__datagramer__](#datagramer) to receive SRT stream if you aren't parsing the raw video.
* use [__fetch__](#fetch) to retrieve files over srt. 
* All other functionality is built into the __srtfu.SRTfu__ class
---
# packetizer
If you've been wondering how to get 188 byte mpegts packets from SRT payloads, use packetizer.
packetizer is a generator that receives a live SRT stream and returns converted and reassembled mpegts packets.
```py3
from srtfu import packetizer

srt_url = 'srt://192.168.5.45:9000'

for packet in packetizer(srt_url):
 print(packet)
...
```
* it's that easy.
---

# datagramer
Use the __datagramer__ function to receive a live srt stream.

```py3
datagramer(srt_url,flags=None)

```
* datagramer takes an srt_url as an arg and returns a generator of raw datagram payloads.

* Complete working example

```py3
import sys
from srtfu import datagramer

srt_url = srt://10.0.0.1:9000

for datagram in datagramer(srt_url):
    sys.stdout.buffer.write(datagram)
```

___
# fetch

If you just want to retrieve files over SRT, use the fetch function. 

```py3
 fetch(srt_url , remote_file, local_file, flags=None)
```

* Complete working example

```py3
from srtfu import fetch

srt_url = srt://206.170.125.43:9000
remote_file = /home/a/video.ts
local_file = video.ts

fetch(srt_url , remote_file, local_file)
```
___

# smoketest
### The smoketest from the libsrt docs.

* create the file livekabuki.py
```py3
#!/usr/bin/env python3

import sys
from  srtfu import datagramer

srt_url = sys.argv[1]
for datagram in datagramer(srt_url):
    sys.stdout.buffer.write(datagram)

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

# SCTE35

### parsing SCTE-35 from an srt stream with threefive

* install [threefive](https://github.com/superkabuki/SCTE35-Kabuki)
  ```py3
  python3 -mpip install threefive --break-system-packages
  ```
* run threefive
```py3
threefive srt://1.2.3.4:4201
```
___


# low level
* Most of libsrt is available in SRTfu, the ctypes conversions are handled for you.
* If you've used sockets, this will all seem very similar.
* One note, the socket is an optional arg in methods, it only needs to be used when a server accepts a socket connection. 
* init SRTfu instance, just provide a srt_url
* a socket is created for you, but not connected.
* the srt_url sets host and port to bind for servers (0.0.0.0 works), and host and port to connect for clients
___
* init SRTfu instance
```py3
from srtfu import SRTfu

srt_url =srt://127.0.0.1:9000

srtf=SRTfu(srt_url)
```
* srt_url can be where an instance is listening, or the address that an instance wants to connect to, everything is in the same class
* When an instance is created  socket, self.sock is created.
* __SRTfu methods will handle all the ctype conversions and pointers__

```
* next you can set sock flags
```py3
    from srtfu import SRTO_TRANSTYPE,SRT_LIVE,SRTO_RCVSYN,SRTO_RCVBUF

    srtf.setsockflag(SRTO_TRANSTYPE,SRT_LIVE)
    srtf.setsockflag(SRTO_RCVSYN,1)
    srtf.setsockflag(SRTO_RCVBUF,3276800)

```
* You can also pass a dict of socket flags to set when you create a new instance of SRTfu
```py3

  from srtfu import SRTfu, SRTO_TRANSTYPE,SRT_LIVE,SRTO_RCVSYN,SRTO_RCVBUF

  flags={SRTO_TRANSTYPE:SRT_LIVE,
         SRTO_RCVSYN:1,
         SRTO_RCVBUF: 3276800,}

  srt_url = srt://127.0.0.1:9000
  srtf=SRTfu(srt_url,flags=flags)
```

* set congestion control algorithm
 ```py3
   srtf.conlive()   # for live
# OR

  srtf.confile()    # for file

# OR to set any type of congestion control

srtf.congestion_control(the_algo)

```
* for clients call connect
```py3
srtf.connect()
```

* SRTfu  also has a __read__ method
```py3
from srtfu import SRTfu

srt_url= 'srt://1.2.3.4:5678'
srtf=SRTfu(srt_url)
srtf.connect()
data = srtf.read(10000)

```
*  for servers call bind and listen
```py3
  srtf.bind()
  srtf.listen()
```
* to accept a connection on a server
```py3
    fhandle = srtf.accept() 
```
* to receive from a client
* Note the socket is always the last arg
```py3
 smallbuff = srtf.mkbuff(1500)
 srtf.recv(smallbuff, fhandle)
```
* If you need a buffer to receive into

```py3
  smallbuff = srtf.mkbuff(1500)
```
* if you need to send data in a buffer

```py3
message = 'message can be strings, bytes, or ints'
new_message= srtf.mkmsg(message)
```


## SRTfu

```py3
Help on class SRTfu in module srtfu.srtfu:

class SRTfu(builtins.object)
 |  SRTfu(srturl, flags=None)
 |  
 |  SRTfu Pythonic Secure Reliable Transport
 |  
 |  Methods defined here:
 |  
 |  __init__(self, srturl, flags=None)
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
 |  confile(self)
 |      confile set congestion control to file
 |  
 |  congestion_control(self, algo)
 |      congestion_control set the congestion control
 |      algorithm. can also be set with livecc() and filecc()
 |      methods.
 |  
 |  conlive(self)
 |      conlive set congestion control to live
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
 |  read(self, numbytes)
 |      read read numbytes of bytes
 |      and return them.
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
 |      remote_file_size read remote file size.
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
 |  setflags(self, flags)
 |      setflags set flags on an SRTfu instance
 |      
 |      flags  a dict of socket flags you want to have set.
 |                 ex. {SRTO_TRANSTYPE: SRT_LIVE,
 |                         SRTO_RCVSYN: 1, }
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


# Socket Flags 
* Note: these are the flag number for the socket, not the value of the flag.
```py3
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

