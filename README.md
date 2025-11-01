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


# SRT API Functions

<h3 id="Library Initialization">Library Initialization</h3>

| *Function / Structure*                            | *Description*                                                    | status                                              |
|:------------------------------------------------- |:-----------------------------------------------------------------|:--------------------------------------------- |
| [srt_startup](#srt_startup)                       | Called at the start of an application that uses the SRT library          | done                                      |
| [srt_cleanup](#srt_cleanup)                       | Cleans up global SRT resources before exiting an application             | done                               |
| <img width=290px height=1px/>                     | <img width=720px height=1px/>                                                                                  |


<h3 id="creating-and-configuring-sockets">Creating and Configuring Sockets</h3>

| *Function / Structure*                            | *Description*                                                     | status                                             |
|:------------------------------------------------- |:------------------------------------------------------------------|:-------------------------------------------- |
| [srt_socket](#srt_socket)                         | Deprecated                                                                | skipped                                     |
| [srt_create_socket](#srt_create_socket)           | Creates an SRT socket                                                     | done                                     |
| [srt_bind](#srt_bind)                             | Binds a socket to a local address and port                                | done                                     |
| [srt_bind_acquire](#srt_bind_acquire)             | Acquires a given UDP socket instead of creating one                       | pending                                     |
| [srt_getsockstate](#srt_getsockstate)             | Gets the current status of the socket                                    | pending                                         |
| [srt_getsndbuffer](#srt_getsndbuffer)             | Retrieves information about the sender buffer                           | pending                                          |
| [srt_close](#srt_close)                           | Closes the socket or group and frees all used resources                 | done                                       |
| <img width=290px height=1px/>                     | <img width=720px height=1px/>                                                                                  |

<h3 id="connecting">Connecting</h3>

| *Function / Structure*                            | *Description*                                                                 | status                                 |
|:------------------------------------------------- |:-------------------------------------------------------------------------|:------------------------------------- |
| [srt_listen](#srt_listen)                         | Sets up the listening state on a socket                                  | done                                      |
| [srt_accept](#srt_accept)                         | Accepts a connection; creates/returns a new socket or group ID          | done                                       |
| [srt_accept_bond](#srt_accept_bond)               | Accepts a connection pending on any sockets passed in the `listeners` array <br/> of `nlisteners` size | pending               |
| [srt_listen_callback](#srt_listen_callback)       | Installs/executes a callback hook on a socket created to handle the incoming connection <br/> on a listening socket  | pending |
| [srt_connect](#srt_connect)                       | Connects a socket or a group to a remote party with a specified address and port       | done                        |
| [srt_connect_bind](#srt_connect_bind)             | Same as [`srt_bind`](#srt_bind) then [`srt_connect`](#srt_connect) if called with socket [`u`](#u) | pending               |
| [srt_connect_debug](#srt_connect_debug)           | Same as [`srt_connect`](#srt_connect)but allows specifying ISN (developers only)  | pending                                |
| [srt_rendezvous](#srt_rendezvous)                 | Performs a rendezvous connection                                                              | pending                    |
| [srt_connect_callback](#srt_connect_callback)     | Installs/executes a callback hook on socket/group [`u`](#u) after connection resolution/failure           | pending        |
| <img width=290px height=1px/>                     | <img width=720px height=1px/>                                                                                  |


<h3 id="helper-data-types-for-transmission">Helper Data Types for Transmission</h3>

| *Function / Structure*                            | *Description*                         | status                                                                          |
|:------------------------------------------------- |:-------------------------------------|:------------------------------------------------------------------------- |
| [SRT_MSGCTRL](#SRT_MSGCTRL)                       | Used in [`srt_sendmsg2`](#srt_sendmsg) and [`srt_recvmsg2`](#srt_recvmsg2) calls; <br/> specifies some extra parameters | done  |
| <img width=290px height=1px/>                     | <img width=720px height=1px/>                                                                                  |

<h3 id="transmission">Transmission</h3>

| *Function / Structure*                            | *Description*                                          | status                                                        |
|:------------------------------------------------- |:-------------------------------------------------------|:------------------------------------------------------- |
| [srt_send](#srt_send)                             | Sends a payload to a remote party over a given socket          | done                                                |
| [srt_sendmsg](#srt_sendmsg)                       | Sends a payload to a remote party over a given socket                | pending                                             |
| [srt_sendmsg2](#srt_sendmsg2)                     | Sends a payload to a remote party over a given socket        | done                                                  |
| [srt_recv](#srt_recv)                             | Extracts the payload waiting to be received                        | done                                            |
| [srt_recvmsg](#srt_recvmsg)                       | Extracts the payload waiting to be received                              | done                                      |
| [srt_recvmsg2](#srt_recvmsg2)                     | Extracts the payload waiting to be received                                    | pending                                |
| [srt_sendfile](#srt_sendfile)                     | Function dedicated to sending a file                                | pending                                           |
| [srt_recvfile](#srt_recvfile)                     | Function dedicated to receiving a file                        | done                                                 |
| <img width=290px height=1px/>                     | <img width=720px height=1px/>                                                                                  |

               |           |          

