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

___

### NEWS
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting SRTO_TRANSTYPE and SRT_SOCKOPT correctly ,but I figured it out today.Super jazzed

___

### To be honest, I don't find libsrt0 super intuitive, so I'm not just wrapping it, I'm trying to make it a bit more friendly. 

<details><summary>Here's the recvfile.cpp from the examples </summary>

```cpp
#ifndef _WIN32
   #include <arpa/inet.h>
   #include <netdb.h>
#else
   #include <winsock2.h>
   #include <ws2tcpip.h>
#endif
#include <fstream>
#include <iostream>
#include <cstdlib>
#include <cstring>
#include <srt.h>

using namespace std;

int main(int argc, char* argv[])
{
   if ((argc != 5) || (0 == atoi(argv[2])))
   {
      cout << "usage: recvfile server_ip server_port remote_filename local_filename" << endl;
      return -1;
   }

   // Use this function to initialize the UDT library
   srt_startup();

   srt_setloglevel(srt_logging::LogLevel::debug);

   struct addrinfo hints, *peer;

   memset(&hints, 0, sizeof(struct addrinfo));
   hints.ai_flags = AI_PASSIVE;
   hints.ai_family = AF_INET;
   hints.ai_socktype = SOCK_DGRAM;

   SRTSOCKET fhandle = srt_create_socket();
   // SRT requires that third argument is always SOCK_DGRAM. The Stream API is set by an option,
   // although there's also lots of other options to be set, for which there's a convenience option,
   // SRTO_TRANSTYPE.
   SRT_TRANSTYPE tt = SRTT_FILE;
   srt_setsockopt(fhandle, 0, SRTO_TRANSTYPE, &tt, sizeof tt);

   if (0 != getaddrinfo(argv[1], argv[2], &hints, &peer))
   {
      cout << "incorrect server/peer address. " << argv[1] << ":" << argv[2] << endl;
      return -1;
   }

   // Connect to the server, implicit bind.
   if (SRT_ERROR == srt_connect(fhandle, peer->ai_addr, peer->ai_addrlen))
   {
      cout << "connect: " << srt_getlasterror_str() << endl;
      return -1;
   }

   freeaddrinfo(peer);

   // Send name information of the requested file.
   int len = strlen(argv[3]);

   if (SRT_ERROR == srt_send(fhandle, (char*)&len, sizeof(int)))
   {
      cout << "send: " << srt_getlasterror_str() << endl;
      return -1;
   }

   if (SRT_ERROR == srt_send(fhandle, argv[3], len))
   {
      cout << "send: " << srt_getlasterror_str() << endl;
      return -1;
   }

   // Get size information.
   int64_t size;

   if (SRT_ERROR == srt_recv(fhandle, (char*)&size, sizeof(int64_t)))
   {
      cout << "send: " << srt_getlasterror_str() << endl;
      return -1;
   }

   if (size < 0)
   {
      cout << "no such file " << argv[3] << " on the server\n";
      return -1;
   }

   // Receive the file.
   int64_t recvsize; 
   int64_t offset = 0;

   SRT_TRACEBSTATS trace;
   srt_bstats(fhandle, &trace, true);

   if (SRT_ERROR == (recvsize = srt_recvfile(fhandle, argv[4], &offset, size, SRT_DEFAULT_RECVFILE_BLOCK)))
   {
      cout << "recvfile: " << srt_getlasterror_str() << endl;
      return -1;
   }

   srt_bstats(fhandle, &trace, true);

   cout << "speed = " << trace.mbpsRecvRate << "Mbits/sec" << endl;
   int losspercent = 100*trace.pktRcvLossTotal/trace.pktRecv;
   cout << "loss = " << trace.pktRcvLossTotal << "pkt (" << losspercent << "%)\n";

   srt_close(fhandle);

   // Signal to the SRT library to clean up all allocated sockets and resources.
   srt_cleanup();

   return 0;
}
```

</details>

<details><summary>Here's my implentation of recvfile, it's not as complete,but it's a bit more concise</summary>

```py3
    def fetch(self, host, port, remote_file, local_file):
        """
        fetch fetch remote_file fron host on port
        and save it as local_file
        """
        yes = ctypes.c_int(1)
        self.setsockflag(SRTO_TRANSTYPE,yes)
        self.connect(host,port)
        self.request_file(remote_file)
        self.recv_file(local_file)
        self.getlasterror()
```

</details>

#### If you don't find my way very intuitive, all the functions are being mapped to methods so you do it almost the same way as libsrt.
* SRTKabuki method names are the libsrt functions without the `srt_` prefix.  
___

### Download a file over SRT with SRTKabuki in three lines of code

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
___

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



