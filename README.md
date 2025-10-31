# Secure Reliable Transport Kabuki
### Call libsrt C functions from python.
<sampl>
I started to convert libsrt to python, then I started reading the ctypes module docs<BR>
and decided it made more sense to call libsrt C function directly from python. <BR>
</sampl>

# Download a file over SRT with SRTKabuki

```py3
Python 3.11.2 (main, Apr 28 2025, 14:11:48) [GCC 12.2.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> from srtkabuki import SRTKabuki
>>> srtk=SRTKabuki()
startup: Success
create_socket: Success
>>> srtk.fetch('10.7.1.3','9000','a_b_c.ts','gonzo.ts')   # host, port, remotefile, localfile
set_sock_flag: Success
request_file: Success
remote_file_size: Success
recv_file: Success
fetch: Success
>>>
```
```



### NEWS
* 10/30/2025 :  __Today I got basic downloading files over a network using SRT working__,cleaning up code for a new commit. 
* 10/29/2025 :  I've been stuck on setting SRTO_TRANSTYPE and SRT_SOCKOPT correctly ,but I figured it out today.Super jazzed

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


### Here's an srt client example included with libsrt.

<details><summary> the original srt client example included with libsrt </summary>
 
```c
  /*
 * SRT - Secure, Reliable, Transport
 * Copyright (c) 2017 Haivision Systems Inc.
 * 
 * This library is free software; you can redistribute it and/or
 * modify it under the terms of the GNU Lesser General Public
 * License as published by the Free Software Foundation; either
 * version 2.1 of the License, or (at your option) any later version.
 * 
 * This library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * Lesser General Public License for more details.
 * 
 * You should have received a copy of the GNU Lesser General Public
 * License along with this library; If not, see <http://www.gnu.org/licenses/>
 */


#include <stdio.h>
#include <stdlib.h>
#ifdef _WIN32
#define usleep(x) Sleep(x / 1000)
#else
#include <unistd.h>
#endif

#include "srt.h"

int main(int argc, char** argv)
{
    int ss, st;
    struct sockaddr_in sa;
    int yes = 1;
    const char message [] = "This message should be sent to the other side";

    if (argc != 3) {
      fprintf(stderr, "Usage: %s <host> <port>\n", argv[0]);
      return 1;
    }

    printf("srt startup\n");
    srt_startup();

    printf("srt socket\n");
    ss = srt_create_socket();
    if (ss == SRT_ERROR)
    {
        fprintf(stderr, "srt_socket: %s\n", srt_getlasterror_str());
        return 1;
    }

    printf("srt remote address\n");
    sa.sin_family = AF_INET;
    sa.sin_port = htons(atoi(argv[2]));
    if (inet_pton(AF_INET, argv[1], &sa.sin_addr) != 1)
    {
        return 1;
    }

    printf("srt setsockflag\n");
    if (SRT_ERROR == srt_setsockflag(ss, SRTO_SENDER, &yes, sizeof yes))
    {
        fprintf(stderr, "srt_setsockflag: %s\n", srt_getlasterror_str());
        return 1;
    }

    // Test deprecated
    //srt_setsockflag(ss, SRTO_STRICTENC, &yes, sizeof yes);

    printf("srt connect\n");
    st = srt_connect(ss, (struct sockaddr*)&sa, sizeof sa);
    if (st == SRT_ERROR)
    {
        fprintf(stderr, "srt_connect: %s\n", srt_getlasterror_str());
        return 1;
    }

    int i;
    for (i = 0; i < 100; i++)
    {
        printf("srt sendmsg2 #%d >> %s\n",i,message);
        st = srt_sendmsg2(ss, message, sizeof message, NULL);
        if (st == SRT_ERROR)
        {
            fprintf(stderr, "srt_sendmsg: %s\n", srt_getlasterror_str());
            return 1;
        }

        usleep(1000);   // 1 ms
    }


    sleep(1); // 1 second to give it enough time to receive all messages
    printf("srt close\n");
    st = srt_close(ss);
    if (st == SRT_ERROR)
    {
        fprintf(stderr, "srt_close: %s\n", srt_getlasterror_str());
        return 1;
    }

    printf("srt cleanup\n");
    srt_cleanup();
    return 0;
}
```

</details>


<details><summary>The srt client example  using SRTKabuki</summary>
  
```py3
    from srtk.py import SRTKabuki

    srtk=SRTKabuki('127.0.0.1',9000)
    srtk.set_sock_flag(SRTO_SENDER)
    srtk.connect()
    a = 100
    while a:
        a -=1
        srtk.write_mesg(b'I am super cool')
    srtk.done()
```

</details>
