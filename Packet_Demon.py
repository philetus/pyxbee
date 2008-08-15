import re
from threading import Thread
from Queue import Queue
from Receive_Packet import Receive_Packet
from Command_Response_Packet import Command_Response_Packet
from Transmit_Response_Packet import Transmit_Response_Packet

class Packet_Demon( Thread ):
    """takes bytes read from serial buffer and parses packet from them
    """
    ESCAPE_PATTERN = re.compile( '\x7d(.)' )

    def __init__( self, name, idle_queue, output_queue ):
        Thread.__init__( self )

        self.name = name
        self.idle_queue = idle_queue
        self.output_queue = output_queue

        self.input_queue = Queue()

        # flag to track whether last byte read was escape character
        self.escaped = False

        # buffer of string read so far
        self.read_buffer = ""

        # packet size to look for
        self.count = None

    def run( self ):
        
        # loop and read from queue
        while self.input_queue:
            raw = self.input_queue.get()

            # reset packet on end of stream delimiter
            if raw is None:
                self._reset_packet()

                # put self back on idle queue to wait for new packet
                self.idle_queue.put( self )

                
            # check that packet has not already been parsed
            elif self.count is True and raw:
                print "%d: read spurious data for completed packet: '%s'" % (
                    self.name, ":".join("%x" % ord(c) for c in raw) )

            # otherwise escape and handle data
            elif raw:

                self.read_buffer += self._escape_data( raw )

                # if there is no count and we have read the first two bytes
                # of the packet calculate count
                if self.count is None and len(self.read_buffer) > 1:
                    self._calculate_count()

                # if we have read count + 1 bytes run checksum and parse packet
                if( self.count is not None
                    and len(self.read_buffer) > self.count ):
                    if not self._test_checksum():
                        print "%d: packet failed checksum: '%s'" % (
                            self.name, self.read_buffer)
                    else:
                        self._parse_packet()

                    # set count to true
                    self.count = True

    def _parse_packet( self ):
        packet = None
        buff = self.read_buffer[:self.count]
        
        # determine packet type from api id
        api_id = ord( buff[0] )

        # receive packet
        if api_id == 0x80 or api_id == 0x81:
            packet = Receive_Packet( buff )

        # response packet
        elif api_id == 0x88:
            packet = Command_Response_Packet( buff )
        elif api_id == 0x89:
            packet = Transmit_Response_Packet( buff )

        else:
            print "%d: unknown packet type received: %x" % (self.name, api_id)
            return

        # put packet on queue
        self.output_queue.put( packet )
                    
    def _reset_packet( self ):
        
        # count is set to true when read buffer reaches count
##        if self.count is not True:
##            print "%d!" % self.name,
##            print "%d: packet stream closed on byte %s/%s: '%s'\n" % (
##                self.name, len(self.read_buffer), str(self.count),
##                ":".join("%x" % ord(c) for c in self.read_buffer) )
            
        self.read_buffer = ""
        self.count = None
        self.escaped = False

    def _test_checksum( self ):  
        checksum = ord( self.read_buffer[self.count] )
        buffer_sum = sum( ord(c) for c in self.read_buffer[:self.count] )
        return ((buffer_sum + checksum) & 0xff) == 0xff
                        
    def _calculate_count( self ):                
        hi, lo = ( ord(c) for c in self.read_buffer[:2] )
        self.count = (hi << 8) + lo
        self.read_buffer = self.read_buffer[2:]

    def _escape_data( self, string ):
        
        # if last character of string is escape character,
        # add it to beginning of next string read
        if self.escaped:
            string = '\x7d' + string
            self.escaped = False
        if string[-1] == '\x7d':
            string = string[:-1]
            self.escaped = True

        # escape string and return
        string = self.ESCAPE_PATTERN.sub( self._escape_match, string )
        return string
    
    @staticmethod
    def _escape_match( match ):        
        return chr( ord(match.group(1)) ^ 0x20 )
