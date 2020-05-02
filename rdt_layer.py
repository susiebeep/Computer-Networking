from segment import Segment


# #################################################################################################################### #
# RDTLayer                                                                                                             #
#                                                                                                                      #
# Description:                                                                                                         #
# The reliable data transfer (RDT) layer is used as a communication layer to resolve issues over an unreliable         #
# channel.                                                                                                             #
#                                                                                                                      #
#                                                                                                                      #
# Notes:                                                                                                               #
# This file is meant to be changed.                                                                                    #
#                                                                                                                      #
#                                                                                                                      #
# #################################################################################################################### #


class RDTLayer(object):
    # ################################################################################################################ #
    # Class Scope Variables                                                                                            #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    DATA_LENGTH = 4 # in characters                     # The length of the string data that will be sent per packet...
    FLOW_CONTROL_WIN_SIZE = 15 # in characters          # Receive window size for flow-control
    sendChannel = None
    receiveChannel = None
    dataToSend = ''
    currentIteration = 0                                # Use this for segment 'timeouts'
    # Add items as needed

    # ################################################################################################################ #
    # __init__()                                                                                                       #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.dataIntoSeg = []
        self.seg = []
        self.sendSize = 1
        self.currentIteration = 0
        self.countSegmentTimeouts = 0
        # Add items as needed

    # ################################################################################################################ #
    # setSendChannel()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable sending lower-layer channel                                                 #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # ################################################################################################################ #
    # setReceiveChannel()                                                                                              #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the unreliable receiving lower-layer channel                                               #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # ################################################################################################################ #
    # setDataToSend()                                                                                                  #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to set the string data to send                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def setDataToSend(self,data):
        self.dataToSend = data

    # ################################################################################################################ #
    # getDataReceived()                                                                                                #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Called by main to get the currently received and buffered string data, in order                                  #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def getDataReceived(self):
        # ############################################################################################################ #
        # Identify the data that has been received...
        myReceivedData = []
        for item in self.seg:
            myReceivedData.append(str(item))     
        myReceivedStr = ''.join(myReceivedData)
        return myReceivedStr

    # ################################################################################################################ #
    # processData()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # "timeslice". Called by main once per iteration                                                                   #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processData(self):
        self.currentIteration += 1
        self.processSend()
        self.processReceiveAndSendRespond()

    # ################################################################################################################ #
    # processSend()                                                                                                    #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment sending tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processSend(self):

        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters

        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)

         if (len(self.dataToSend) != 0):
            # check what acks have been sent back by the server
            received = self.receiveChannel.receive()
            nextSeg = 1
            for item in received:
                print("ack received in manageSend:", item.acknum)
                # save the acknum that has been returned as the next sequence number to send
                nextSeg = item.acknum

            # split the data into substrings of length 4 (DATA_LENGTH)
            self.dataIntoSeg = [self.dataToSend[i:i+(self.DATA_LENGTH)] for i in range(0, len(self.dataToSend), self.DATA_LENGTH)]
            
            
            # set the seqNo of the newly created segments based on acks received
            seqNo = nextSeg;
            # get the index of the next segment to send from dataIntoSeg by dividing sequence number by length of segment (4)
            nextSeg = nextSeg // self.DATA_LENGTH   

            # set the limit of the number of segs to send to 3 (flow control window is 15 chars, each segment is 4 chars so it can only
            # accomodate 3 segments at a time) 
            segsToSend = self.dataIntoSeg[nextSeg:nextSeg + 3]
            
            # convert substrings into segments and set their data and sequence numbers     
            for item in segsToSend:
                newseg = Segment()
                newseg.setData(seqNo, item)
                 # append segment to seg member variable
                self.seg.append(item)
                seqNo+=self.DATA_LENGTH
          
                print("sending segment: ")
                newseg.printToConsole()
                        
                # Use the unreliable sendChannel to send the segment
                self.sendChannel.send(newseg)
                
                # delay the sending of the segment by 3 iterations
                #newseg.setStartDelayIteration(3)
               
            # wait for acknum from receiver before sending next burst of segments    
            # acknum received must equal lastSeqNo
            
            # countdown timer run out, re-send segment   

    # ################################################################################################################ #
    # processReceive()                                                                                                 #
    #                                                                                                                  #
    # Description:                                                                                                     #
    # Manages Segment receive tasks                                                                                    #
    #                                                                                                                  #
    #                                                                                                                  #
    # ################################################################################################################ #
    def processReceiveAndSendRespond(self):
        segmentAck = Segment()                  # Segment acknowledging packet(s) received

        # This call returns a list of incoming segments (see Segment class)...
        listIncoming = self.receiveChannel.receive()

         # get the ack number for the last segment sent and save a copy of the data received
        # in a new list
        if (len(listIncoming) != 0):
            acknum = 0
            incomingData = []
            for item in listIncoming:
                acknum = item.seqnum + self.DATA_LENGTH
                incomingData.append(item.payload)
                boolChecksum = item.checkChecksum()
                if (boolChecksum == False):
                    print("checksums don't match")
                    #send back sequence number of corrupted segment for selective retransmission
                    self.sendChannel.send(item.seqnum)
        
            #create the ack segment with a copy of the list of data received and an cumulative ack number
            ack = Segment()
            ack.setAck(acknum)
        
            for item in incomingData:
                self.seg.append(item)          
        
            # Use the unreliable sendChannel to send the ack packet
            self.sendChannel.send(ack)
            print("sending ack:")
            ack.printToConsole() 
   
