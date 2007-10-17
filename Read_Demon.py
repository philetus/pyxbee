from threading import Thread
from time import sleep

from Receive_Packet import Receive_Packet

class Read_Demon( Thread ):

    def __init__( self, queue, port, port_lock ):
        Thread.__init__( self )
        self.queue = queue
        self.port = port
        self.port_lock = port_lock
        self.buffer = []

    def run( self ):

        buff = []
        escape_next = False
        count_state = 0 # 0 - need delimiter, 1 - need high, 2 - need low, 3
        count = 0
        
        # loop and read from serial port
        while self.port:
            waiting = self.port.inWaiting()

            # don't race while there is no data
            if waiting < 1:
                sleep( 0.1 )

            else:
                self.port_lock.acquire()
                try:
                    raw = self.port.read(waiting)

                    # escape data and place on buffer
                    for c in raw:

                        # look for delimiter
                        if count_state == 0:
                            if ord(c) == 0x7e:
                                count_state = 1

                        # get count
                        elif count_state == 1:
                            count = ord(c) * 256
                            count_state = 2
                        elif count_state == 2:
                            count += ord(c)
                            count_state = 3

                        # capture bytes up to count
                        else:
                            if escape_next:
                                escape_next = False
                                buff.append( ord(c) ^ 0x20 )
                            elif ord(c) == 0x7d:
                                escape_next = True
                            else:
                                buff.append( ord(c) )

                            # parse packet from data buffer
                            if len(buff) == count:
                                self._parse_packet( buff )
                                buff = []
                                count_state = 0
                                count = 0

                finally:
                    self.port_lock.release()
                    
    def _parse_packet( self, buff ):
        print "parsing", buff

        # identify packet type and place it on buffer
        if buff[0] == 0x80 or buff[0] == 0x81:
            packet = Receive_Packet( buff )
            self.queue.put( packet )

        elif buff[0] == 0x88:
            packet = Command_Response( buff )
            self.queue.put( packet )

        else:
            print "unknown packet type received:", buff[0]
