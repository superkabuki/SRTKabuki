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


