"""
srtfu.__init__.py

socket flags and assorted constants included here.

"""

import socket

from enum import IntEnum

"""
constants from srt.h
"""


SRT_ERROR = -1

AF_INET = socket.AF_INET

SOCK_DGRAM = socket.SOCK_DGRAM

AI_PASSIVE = socket.AI_PASSIVE

SRT_DEFAULT_RECVFILE_BLOCK = 7200

SRT_LIVE_DEF_PLSIZE = 1316

SRT_LIVE_MAX_PLSIZE = 1456

SRT_LIVE_DEF_LATENCY_MS = 120


# SRT_TRANSTYPE

SRT_LIVE = 0

SRT_FILE = 1

SRT_INVALID = 2


"""
these are the SRT socket options.
libsrt has them in an enum,
but I like being able to do

from srtfu import  SRTO_RCVSYN
"""

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


class SRTTransType(IntEnum):
    SRTT_LIVE=0
    SRTT_FILE=1
    SRTT_INVALID=2


class SRTSockStatus(IntEnum): 
    SRTS_INIT = 1
    SRTS_OPENED=2
    SRTS_LISTENING=3
    SRTS_CONNECTING=4
    SRTS_CONNECTED=5
    SRTS_BROKEN=6
    SRTS_CLOSING=7
    SRTS_CLOSED=8
    SRTS_NONEXIST=9


class SRTSockOpt(IntEnum): 
    SRTO_MSS = 0             # the Maximum Transfer Unit
    SRTO_SNDSYN = 1          # if sending is blocking
    SRTO_RCVSYN = 2          # if receiving is blocking
    SRTO_ISN = 3             # Initial Sequence Number (valid only after srt_connect or srt_accept-ed sockets)
    SRTO_FC = 4              # Flight flag size (window size)
    SRTO_SNDBUF = 5          # maximum buffer in sending queue
    SRTO_RCVBUF = 6          # UDT receiving buffer size
    SRTO_LINGER = 7          # waiting for unsent data when closing
    SRTO_UDP_SNDBUF = 8      # UDP sending buffer size
    SRTO_UDP_RCVBUF = 9      # UDP receiving buffer size
    # (some space left)
    SRTO_RENDEZVOUS = 12     # rendezvous connection mode
    SRTO_SNDTIMEO = 13       # send() timeout
    SRTO_RCVTIMEO = 14       # recv() timeout
    SRTO_REUSEADDR = 15      # reuse an existing port or create a new one
    SRTO_MAXBW = 16          # maximum bandwidth (bytes per second) that the connection can use
    SRTO_STATE = 17          # current socket state see SRT_SOCKSTATUS read only
    SRTO_EVENT = 18          # current available events associated with the socket
    SRTO_SNDDATA = 19        # size of data in the sending buffer
    SRTO_RCVDATA = 20        # size of data available for recv
    SRTO_SENDER = 21         # Sender mode (independent of conn mode) for encryption tsbpd handshake.
    SRTO_TSBPDMODE = 22      # Enable/Disable TsbPd. Enable -> Tx set origin timestamp Rx deliver packet at origin time + delay
    SRTO_LATENCY = 23        # NOT RECOMMENDED. SET: to both SRTO_RCVLATENCY and SRTO_PEERLATENCY. GET: same as SRTO_RCVLATENCY.
    SRTO_INPUTBW = 24        # Estimated input stream rate.
    SRTO_OHEADBW             # MaxBW ceiling based on % over input stream rate. Applies when UDT_MAXBW=0 (auto).
    SRTO_PASSPHRASE = 26     # Crypto PBKDF2 Passphrase (must be 10..79 characters or empty to disable encryption)
    SRTO_PBKEYLEN            # Crypto key len in bytes {162432} Default: 16 (AES-128)
    SRTO_KMSTATE             # Key Material exchange status (UDT_SRTKmState)
    SRTO_IPTTL = 29          # IP Time To Live (passthru for system sockopt IPPROTO_IP/IP_TTL)
    SRTO_IPTOS=30               # IP Type of Service (passthru for system sockopt IPPROTO_IP/IP_TOS)
    SRTO_TLPKTDROP = 31      # Enable receiver pkt drop
    SRTO_SNDDROPDELAY = 32   # Extra delay towards latency for sender TLPKTDROP decision (-1 to off)
    SRTO_NAKREPORT = 33      # Enable receiver to send periodic NAK reports
    SRTO_VERSION = 34        # Local SRT Version
    SRTO_PEERVERSION         # Peer SRT Version (from SRT Handshake)
    SRTO_CONNTIMEO = 36      # Connect timeout in msec. Caller default: 3000 rendezvous (x 10)
    SRTO_DRIFTTRACER = 37    # Enable or disable drift tracer
    SRTO_MININPUTBW = 38     # Minimum estimate of input stream rate.
    # (some space left)
    SRTO_SNDKMSTATE = 40     # (GET) the current state of the encryption at the peer side
    SRTO_RCVKMSTATE=41          # (GET) the current state of the encryption at the agent side
    SRTO_LOSSMAXTTL=42          # Maximum possible packet reorder tolerance (number of packets to receive after loss to send lossreport)
    SRTO_RCVLATENCY=43          # TsbPd receiver delay (mSec) to absorb burst of missed packet retransmission
    SRTO_PEERLATENCY=44         # Minimum value of the TsbPd receiver delay (mSec) for the opposite side (peer)
    SRTO_MINVERSION=45          # Minimum SRT version needed for the peer (peers with less version will get connection reject)
    SRTO_STREAMID=46            # A string set to a socket and passed to the listener's accepted socket
    SRTO_CONGESTION=47          # Congestion controller type selection
    SRTO_MESSAGEAPI=48          # In File mode use message API (portions of data with boundaries)
    SRTO_PAYLOADSIZE=49         # Maximum payload size sent in one UDP packet (0 if unlimited)
    SRTO_TRANSTYPE = 50      # Transmission type (set of options required for given transmission type)
    SRTO_KMREFRESHRATE=51       # After sending how many packets the encryption key should be flipped to the new key
    SRTO_KMPREANNOUNCE=52       # How many packets before key flip the new key is annnounced and after key flip the old one decommissioned
    SRTO_ENFORCEDENCRYPTION=53  # Connection to be rejected or quickly broken when one side encryption set or bad password
    SRTO_IPV6ONLY=54            # IPV6_V6ONLY mode
    SRTO_PEERIDLETIMEO=55       # Peer-idle timeout (max time of silence heard from peer) in [ms]
    SRTO_BINDTODEVICE=56        # Forward the SOL_SOCKET/SO_BINDTODEVICE option on socket (pass packets only from that device)
    SRTO_GROUPCONNECT=57        # Set on a listener to allow group connection (ENABLE_BONDING)
    SRTO_GROUPMINSTABLETIMEO=58 # Minimum Link Stability timeout (backup mode) in milliseconds (ENABLE_BONDING)
    SRTO_GROUPTYPE=59           # Group type to which an accepted socket is about to be added available in the handshake (ENABLE_BONDING)
    SRTO_PACKETFILTER = 60   # Add and configure a packet filter
    SRTO_RETRANSMITALGO = 61 # An option to select packet retransmission algorithm
    SRTO_CRYPTOMODE = 62     # Encryption cipher mode (AES-CTR AES-GCM ...).
    SRTO_MAXREXMITBW = 63    # Maximum bandwidth limit for retransmision (Bytes/s)
    SRTO_E_SIZE=64 # Always last element not a valid option.



# these come after the constants to avoid circular references.

from .srtfu import SRTfu
from .funcs import datagramer, packetizer, fetch
