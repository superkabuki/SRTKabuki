#   1316 or 1456?

That's a good question. With MPEGTS over UDP Unicast and Multicast datagrams are 1316. MPEGTS packets are 188 so 1316 gives you 7 of them. 
<BR>

___

### Gums sending 1316
I wrote a multicast sender Gums, the datagrams are 1316. That's 7 MPEGTS packets and the packets are datagram aligned, meaning datagrams always start at the begining of a packet 
and end at the end of a packet.
<BR><BR>
<img width="988" height="443" alt="image" src="https://github.com/user-attachments/assets/9e130fd3-6de3-4ef4-ae1d-9537a73be268" />
<BR>

___

### libsrt srt-live-transmit sending 1316

I used the srt-live-transmit tool that comes with libsrt. It starts off well , (1332 is 1316 + 16 byte SRT header) but then you can see the sizes start to drift. 

<BR>

<img width="925" height="491" alt="image" src="https://github.com/user-attachments/assets/56c8ae0c-b1db-46c9-a7a0-44a5e674cfae" />
<BR><BR>

---

### How SRTfu works
SRTfu does not care if it's 1316, or 1456,or 5 bytes. when data is received in a buffer, the data is immediately appended to another buffer,
bigfatbuff, when bigfatbuff is over 188 bytes, SRTfu looks for the MPEGTS sync byte and if found, starts slicing off packets.
This approach works very well, and is actually faster and doesn't care what size data is in the buffer.
<BR>

* Here's the code in the packetizer function

```py3
def packetizer(srt_url,flags=None):
    """
    packetizer  mpegts packet generator
    """
    bigfatbuff=b''  
    for datagram in datagramer(srt_url,flags):
        bigfatbuff += datagram.rstrip(ZERO) 
        while SYNC_BYTE in bigfatbuff:           
            bigfatbuff = bigfatbuff[bigfatbuff.index(SYNC_BYTE) :]
            packet, bigfatbuff = bigfatbuff[:PKTSZ], bigfatbuff[PKTSZ:] # slice off a packet
            if verified(packet):  
                yield packet
```
___

###  That's why SRTfu tries to read 1456 at a time, or as much as possible
