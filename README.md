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
* 11/01/2025 :  rewrote examples test-c-server.c and test-c-client.c, using SRTKabuki and they both work. 
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting SRTO_TRANSTYPE and SRT_SOCKOPT correctly ,but I figured it out today.Super jazzed
___

### SRTKabuki is classy.
* No matter what you're doing, you start with
```py3
from srtkabuki import SRTKabuki

srtk = SRTKabuki(addr,port)

```
___
### Examples 
look in the examples directory to see the original c/c++ examples and the rewrites using SRTKabuki.

# Here's where I'm at so far.

```py3
Help on class SRTKabuki in module srtkabuki:

class SRTKabuki(builtins.object)
 |  SRTKabuki(addr='0.0.0.0', port=9000)
 |  
 |  Methods defined here:
 |  
 |  __init__(self, addr='0.0.0.0', port=9000)
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
 |  connect(self)
 |      connect connect to  host on port
 |  
 |  create_socket(self)
 |      create_socket srt_create_socket
 |      and return it
 |  
 |  fetch(self, remote_file, local_file)
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
 |  recv(self)
 |      recv srt_recv
 |  
 |  recvfile(self, local_filename)
 |      recvfile srt_recvfile
 |  
 |  recvmsg(self, msg_buffer)
 |      recvmsg srt_recvmsg
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
```
