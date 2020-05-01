# Sources used:
# Python Split String into Specific Length Chunks, Python Examples, https://pythonexamples.org/python-split-string-into-specific-length-chunks/
# Python For Loops, W3 Schools, https://www.w3schools.com/python/python_for_loops.asp
# How to check if list is empty, Stack Overflow, https://stackoverflow.com/questions/53513/how-do-i-check-if-a-list-is-empty
# K & R Chapter 3.1 - 3.3, 3.5
from unreliable import * 

class RDTLayer(object):
    # The length of the string data that will be sent per packet...
    DATA_LENGTH = 4 # characters
    # Receive window size for flow-control
    FLOW_CONTROL_WIN_SIZE = 15 # characters

    # Add class members as needed...
    #
    def __init__(self):
        self.sendChannel = None
        self.receiveChannel = None
        self.dataToSend = ''
        self.dataIntoSeg = []
        self.seg = []
        self.currentIteration = 0 # <--- Use this for segment 'timeouts'
        self.countSegmentTimeouts = 0

    # Called by main to set the unreliable sending lower-layer channel
    def setSendChannel(self, channel):
        self.sendChannel = channel

    # Called by main to set the unreliable receiving lower-layer channel
    def setReceiveChannel(self, channel):
        self.receiveChannel = channel

    # Called by main to set the string data to send
    def setDataToSend(self,data):
        self.dataToSend = data

    # Called by main to get the currently received and buffered string data, in order
    def getDataReceived(self):
        myReceivedData = []
        for item in self.seg:
            myReceivedData.append(str(item));     
        myReceivedStr = ''.join(myReceivedData);
        return myReceivedStr;

    # "timeslice". Called by main once per iteration
    def manage(self):
        self.currentIteration += 1
        self.manageSend()
        self.manageReceive()

    # Manage Segment sending  tasks...
    def manageSend(self):
        # You should pipeline segments to fit the flow-control window
        # The flow-control window is the constant RDTLayer.FLOW_CONTROL_WIN_SIZE
        # The maximum data that you can send in a segment is RDTLayer.DATA_LENGTH
        # These constants are given in # characters
        
        # Somewhere in here you will be creating data segments to send.
        # The data is just part of the entire string that you are trying to send.
        # The seqnum is the sequence number for the segment (in character number, not bytes)
        
        # split the data into substrings of length 4 (DATA_LENGTH)
        self.dataIntoSeg = [self.dataToSend[i:i+(self.DATA_LENGTH)] for i in range(0, len(self.dataToSend), self.DATA_LENGTH)]
        
        
        # convert substrings into segments and set their data and sequence numbers  
        seqNo = 1;
        sendCount = 0;
        
        for item in self.dataIntoSeg:
            newseg = Segment()
            newseg.setData(seqNo, item)
            print("sending segment: ")
            newseg.dump()
            # Use the unreliable sendChannel to send the segment
            self.sendChannel.send(newseg)
            # start the timer for each segment (100 iterations)
            # newseg.setStartIteration(100)
              
            # append segment to seg member variable
            self.seg.append(item)
            seqNo+=self.DATA_LENGTH
            
            # add one to the send count
            sendCount+= 1
        
        # send a burst of packets, ensuring not to send more than the receive window for the receiver (FLOW_CONTROL_WIN_SIZE)
        # while (sendCount < self.FLOW_CONTROL_WIN_SIZE):    
          
        # set last sequence number to be the sequence number of the last byte sent (should match 
        # ack number sent by receiver)
        # lastSeqNo = seqNo;
           
        # wait for acknum from receiver before sending next burst of segments    
        # acknum received must equal lastSeqNo
        
        # countdown timer run out, re-send segment    


    # Manage Segment receive  tasks...
    def manageReceive(self):
        # This call returns a list of incoming segments (see Segment class)...
        listIncoming = self.receiveChannel.receive()
        # How can you tell data segments apart from ack segemnts?
        
        # Somewhere in here you will be creating ack segments to send.
        # The goal is to employ cumulative ack, just like TCP does...
        
        # if incoming segment list is not empty, get sequence number of last byte plus it's length to set cumulative ack number
        #if (len(listIncoming) == 0):
        #    print("in manageReceive: no data received")
        #else:
        for item in listIncoming:
            ack = Segment()
            acknum = item.seqnum + self.DATA_LENGTH    
            ack.setAck(acknum)
            self.seg.append(item.payload)
        
            # Use the unreliable sendChannel to send the ack packet
            self.sendChannel.send(ack)
            print("sending ack:")
            ack.dump()    
