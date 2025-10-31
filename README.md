# Secure Reliable Transport Kabuki
### Call libsrt C functions from python.

### My goal here is to be able to use the SRT protocol in python 
and to do so with just a few lines of code.
<BR> 

### SRTKabuki is a python class that implements SRT. <BR>

I've just started writing SRTKabuki it's not complete, <BR>
A lot of the base functionality has already been implemented though.<br>

###  Get invovled or go away.

If you are interested in using SRT from python, come work on it with me..<BR>
You don't need to be a master of python, there's stuff to do besides just writing code.<BR>
If you're interested in or know SRT, come on and give me a hand so we can do it much faster.


### NEWS
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting SRTO_TRANSTYPE and SRT_SOCKOPT correctly ,but I figured it out today.Super jazzed


# Download a file over SRT with SRTKabuki in three lines of code

```py3
Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from srtkabuki import SRTKabuki    # 1
>>> srtk=SRTKabuki()                   # 2
startup: Success
create_socket: Success
>>> srtk.fetch('10.7.1.3','9000','a_b_c.ts','gonzo.ts')   # 3      host, port, remotefile, localfile
set_sock_flag: Success
request_file: Success
remote_file_size: Success
recv_file: Success
fetch: Success
>>>
```


# Here's where I'm at so far.
```py3
Help on class SRTKabuki in module srtkabuki:

class SRTKabuki(builtins.object)
 |  Methods defined here:
 |  
 |  __init__(self)
 |      Initialize self.  See help(type(self)) for accurate signature.
 |  
 |  accept(self)
 |      accept srt_accept
 |  
 |  bind(self)
 |      bind  srt_bind
 |  
 |  bytemsg(self, msg)
 |      bytemsg convert python byte string
 |      to a C string buffer
 |  
 |  cleanup(self)
 |      cleanup srt_cleanup
 |  
 |  close(self)
 |      close srt_close
 |  
 |  connect(self, host, port)
 |      connect connect to  host on port
 |  
 |  create_socket(self)
 |      create_socket srt_create_socket
 |      and return it
 |  
 |  fetch(self, host, port, remote_file, local_file)
 |      fetch fetch remote_file fron host on port
 |      and save it as local_file
 |  
 |  getlasterror(self)
 |      getlasterror srt_getlasterror_str
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
 |  mk_sockaddr_ptr(self)
 |      mk_sockaddr_sa make a c compatible (struct sockaddr*)&sa
 |  
 |  recv_file(self, local_file)
 |      recv_file receive a file and write it to local_file
 |   
 |  recvmsg(self)
 |      recvmsg srt_recvmsg
 |  
 |  remote_file_size(self)
 |      remote_file_size receive a message from a server
 |      with the size of the file just requested.
 |  
 |  request_file(self, remote_file)
 |      request_file request a file from a server
 |  
 |  send(self, msg)
 |      send srt_send
 |  
 |  sendmsg2(self, msg)
 |      sendmsg2 format byte string for C
 |      and write it to the socket
 |  
 |  setsockflag(self, flag, val)
 |      setsockflag  setsockflag
 |      the flag is one from statiic.SRT_SOCKOPTS
 |      flag is set to val
 |  
 |  startup(self)
 |      startup  srt_startup()


DATA

    AF_INET = <AddressFamily.AF_INET: 2>
    AI_PASSIVE = <AddressInfo.AI_PASSIVE: 1>
    SOCK_DGRAM = <SocketKind.SOCK_DGRAM: 2>
    SRTO_BINDTODEVICE = 56
    SRTO_CONGESTION = 47
    SRTO_CONNTIMEO = 36
    SRTO_CRYPTOMODE = 62
    SRTO_DRIFTTRACER = 37
    SRTO_ENFORCEDENCRYPTION = 53
    SRTO_EVENT = 18
    SRTO_FC = 4
    SRTO_GROUPCONNECT = 57
    SRTO_GROUPMINSTABLETIMEO = 58
    SRTO_GROUPTYPE = 59
    SRTO_INPUTBW = 24
    SRTO_IPTOS = 30
    SRTO_IPTTL = 29
    SRTO_IPV6ONLY = 54
    SRTO_ISN = 3
    SRTO_KMPREANNOUNCE = 52
    SRTO_KMREFRESHRATE = 51
    SRTO_KMSTATE = 28
    SRTO_LATENCY = 23
    SRTO_LINGER = 7
    SRTO_LOSSMAXTTL = 42
    SRTO_MAXBW = 16
    SRTO_MAXREXMITBW = 63
    SRTO_MESSAGEAPI = 48
    SRTO_MININPUTBW = 38
    SRTO_MINVERSION = 45
    SRTO_MSS = 0
    SRTO_NAKREPORT = 33
    SRTO_OHEADBW = 25
    SRTO_PACKETFILTER = 60
    SRTO_PASSPHRASE = 26
    SRTO_PAYLOADSIZE = 49
    SRTO_PBKEYLEN = 27
    SRTO_PEERIDLETIMEO = 55
    SRTO_PEERLATENCY = 44
    SRTO_PEERVERSION = 35
    SRTO_RCVBUF = 6
    SRTO_RCVDATA = 20
    SRTO_RCVKMSTATE = 41
    SRTO_RCVLATENCY = 43
    SRTO_RCVSYN = 2
    SRTO_RCVTIMEO = 14
    SRTO_RENDEZVOUS = 12
    SRTO_RETRANSMITALGO = 61
    SRTO_REUSEADDR = 15
    SRTO_SENDER = 21
    SRTO_SNDBUF = 5
    SRTO_SNDDATA = 19
    SRTO_SNDDROPDELAY = 32
    SRTO_SNDKMSTATE = 40
    SRTO_SNDSYN = 1
    SRTO_SNDTIMEO = 13
    SRTO_STATE = 17
    SRTO_STREAMID = 46
    SRTO_SNDTIMEO = 13
    SRTO_STATE = 17
    SRTO_STREAMID = 46
    SRTO_TLPKTDROP = 31
    SRTO_TRANSTYPE = 50
    SRTO_TSBPDMODE = 22
    SRTO_UDP_RCVBUF = 9
    SRTO_UDP_SNDBUF = 8
    SRTO_VERSION = 34
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



