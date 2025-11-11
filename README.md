# `S`ecure `R`eliable `T`ransport `Kabuki`
### Call libsrt C functions from python.

### My goal here is to be able to use the SRT protocol in python 
and to do so with just a few lines of code.
<BR> 
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
* 11/08/2025 : __Boom goes the dynamite, reading srt output from srt-live-transmit now works.__
* 11/05/2025 : It's porting pretty smooth, __cyclomatic complexity__ so far is __1.09__, that is sweet..
* 11/04/2025 : started on epoll stuff. it's really started coming together, a couple more weeks to a release I think.
* 11/01/2025 :  rewrote examples test-c-server.c and test-c-client.c, using SRTKabuki and they both work. 
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting SRTO_TRANSTYPE and SRT_SOCKOPT correctly ,but I figured it out today.Super jazzed
___



### Examples
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

look in the examples directory to see the original c/c++ examples and the rewrites using SRTKabuki.
___


# Here's where I'm at so far.

```py3
Help on class SRTKabuki in module srtkabuki:
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
 |  bytemsg(self, msg)
 |      bytemsg convert python byte string
 |      to a C string buffer
 |  
 |  chk_sock(self, sock)
 |      chk_sock if we don't have a sock, use self.sock
 |  
 |  cleanup(self)
 |      cleanup srt_cleanup
 |  
 |  close(self, sock=None)
 |      close srt_close
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
 |  epoll_wait(self, readfds, writefds, ms_timeout, lrds, lwrds)
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
 |  mkbuff(self, buffsize)
 |      mkbuff make a c function compatible buffer
 |  
 |  recv(self, buffer)
 |      recv srt_recv
 |  
 |  recvfile(self, local_filename, sock=None)
 |      recvfile srt_recvfile
 |  
 |  recvmsg(self, buffer, sock=None)
 |      recvmsg srt_recvmsg
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

```
