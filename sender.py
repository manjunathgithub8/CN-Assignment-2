import hashlib
import time
from socket import *
import sys

win = int(sys.argv[1])                        # window size
maxseq = int(sys.argv[2])                     # max sequence number
n = int(sys.argv[3])                          # NO.of packets
I = int(sys.argv[4])                          # every I'th packet loss
timeout = float(sys.argv[5])                  # timeout in sec
revname = sys.argv[6]                         # receiver IP addr
revport = int(sys.argv[7])                    # port Num

if maxseq < win:                              # seq number must be at least equal to window size or more
    print("Sequence number must be greater or equal to the window size\n" );
    exit(0)
soc = socket(AF_INET, SOCK_DGRAM)             # creating Socket
soc.settimeout(0.02)                          # setting socket timeout while receiving

base = 1
seqnum = 0
packetnum = 1

lastrecv = 0
i = 0
sent = []
count = 1
lc = 0
expecrev = []

while packetnum <= n:                                # Stops when last packet is received

    while packetnum < base+win and packetnum<=n:     # to send no.of packets equal to window size at a time

        if count%I == 0:                              # very I'th packet is Not Sent/available to the receiver
            msg = "MESSAGE NUMBER "+str(packetnum)
            checksum = hashlib.md5(msg.encode())       # finding checksum
            print("- Lost",seqnum,";",msg,";",checksum.hexdigest())            # printing the I'th packet lost
            seqnum = packetnum%(maxseq+1)              # update seq num
            packetnum += 1                             # update packet number
            count+=1

        if packetnum < base+win and packetnum<=n :          # checking again after updating the seq number
            msg = "MESSAGE NUMBER "+str(packetnum)          # message content of the packet with packet number
            checksum = hashlib.md5(msg.encode())            # finding checksum using md5 lib
            msg=str(seqnum)+" ; "+msg+" ; "+checksum.hexdigest()  # creating the packet
            soc.sendto(msg.encode('ascii'),(revname, revport))    # Sending packet to receiver
            print("sent "+msg)               # printing msg to console
            sent.append([seqnum,packetnum])                       # appending to sent list for referring later in ack
            seqnum=packetnum%(maxseq+1)                           # update seq num
            packetnum += 1                                        # update pack num
            count+=1                                              # update count


    timecount = time.time()                                       # start timer


    lc = 0

    # To Receive Acknowledgement
    while lc < win:                                    # No.of ack expected to receive is equal to win size(sent packs)
        try:                                           # to handle receive timeout error
            rmsg, raddr = soc.recvfrom(2048)           # receiving Acknowledgement from receiver
            ackmsg=rmsg.decode('ascii')                # decode the message
            acknum=ackmsg.split(" ")                   # get Seq num of Ack

        except :
            while time.time()-timecount < timeout:     # waiting for timeout Sec
                continue
            if lastrecv!=n :                           # resend packets except case where nth pack is received
                print("\nResending packets\n")
            break
        expecrev=sent[i]                               # expected seq num of ack
        if int(acknum[1]) == expecrev[0]:              # check is crct ack is received
            print("return msg : ", ackmsg)             # print ack msg to console
            lastrecv += 1                              # update last received ack for a packet in order
            i += 1
            base += 1                                  # update base

        else:                                            # if wrong acknowledgement is received
            print("return msg : Duplicate Ack Received")
            sent.pop(i)                                  # pop the latest sent packet which is out of order

        lc += 1
    packetnum = lastrecv + 1                             # get Next packet number to send, using last received packet
    seqnum = (packetnum - 1) % (maxseq + 1)              # seq Num of next packet




soc.close()                                              # close socket after receving N'th Packet ack