import sys
from socket import *

maxseq = int(sys.argv[1])                              # max seq number
k = int(sys.argv[2])                                   # buffer size
port = int(sys.argv[3])                                # port number

sock = socket(AF_INET, SOCK_DGRAM)                     # creating a socket
sock.bind(('', port))                                  # binding a port number
print("ready:")

i = 1                                                  # packet index
expecseq = 0
recv = []
j = 0                                                  # index to access buffer messages
buffer = [None]*k                                      # stores message

while True:
    msg,caddr= sock.recvfrom(2048)                    # receiving packet from sender
    msg = msg.decode('ascii')                         # decoding to ascii
    recv=msg.split(" ")                               # splitting to get Sequence Number
    if expecseq == int(recv[0]):                      # checking if expected Seq Num is Received
        buffer[j]=int((recv[0]))                      # store the message in buffer
        msg1="Ack-For-seq "+str(expecseq)             # acknowledgement message
        print("\n"+msg+"\n"+"Packet "+str(i)+" received, sending ack\n")      # print received msg
        expecseq=(expecseq+1)%(maxseq+1)                                       # increment Seq num
        sock.sendto(msg1.encode('ascii'), caddr)                               # Send acknowledgement
        i += 1
        j=(j+1)%k                                                              # increment buffer index

    else:                                                                      # if Wrong packet is Received
                                                                               # (out of order)
        print(msg + "\npacket rejected, OUT OF ORDER ");                       # Drop the packet and print
        print("Packet-of-Seq-Number " + str(expecseq) + " Expected\n")
        msg1="Ack_For_Sequence-No_Up-To: "+str(buffer[(j-1)%k])                # cumulative acknowledgement of
                                                                               # last received pack in order
        print(msg1,"sent\n")
        sock.sendto(msg1.encode('ascii'), caddr)                               # Send the ack

sock.close()                                                                   # close socket for error

