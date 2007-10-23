from serial import Serial
from Queue import Queue, Empty
from threading import Thread, Lock
from time import sleep

from Receive_Packet import Receive_Packet
from Command_Response_Packet import Command_Response_Packet
from Transmit_Response_Packet import Transmit_Response_Packet
from Transmit_Packet import Transmit_Packet
from Command_Packet import Command_Packet

class Xbee( Thread ):
    """library to control xbee in api mode
    """

    def __init__( self, port="/dev/ttyUSB0", timeout=0.1 ):
        Thread.__init__( self )

        # open serial port
        self.port = Serial( port=port, timeout=timeout )

        # xbee ignores first thing you write to it?
        self.port.write( "X" )
        sleep( 0.3 )

        self.write_queue = Queue()
        self.read_queue = Queue()

        # response farm to store command response queues by data frame
        self.response_farm = {}
        self.farm_lock = Lock() # lock to protect response farm access

        # counter for frame ids
        self.frame_counter = 1

        # state for reading packets
        self.read_buff = []
        self.escape_next = False
        self.count_state = 0 # 0 - need delimiter, 1 - need high, 2 - need low, 3
        self.count = 0


    def run( self ):
        while self.port:

            # try to get a packet from write queue
            try:
                packet = self.write_queue.get_nowait()
                self._write_to_serial( packet )
            except Empty:
                pass

            # try to read data from serial port
            waiting = self.port.inWaiting()
            if waiting == 0:
                sleep( 0.1 )
            else:
                raw = self.port.read( waiting )
                self._process_data( [ord(c) for c in raw] )                
        
    def read( self, timeout=1 ):
        """read packet from xbee
        """
        return self.read_queue.get( timeout=timeout )

    def write( self, packet ):
        """write packet to xbee
        """
        self.write_queue.put( packet )

    def get_response( self, packet, timeout=1.0 ):
        """block until response from packet is received
        """
        # wait for response
        response = None
        try:
            response = packet.response_queue.get( timeout=timeout )
        except Empty:
            raise IOError( "no response from xbee for packet frame id %s!"
                           % str(packet.frame_id) )
        
        # remove packet from response farm
        self.farm_lock.acquire()
        try:
            if packet.frame_id in self.response_farm:
                del self.response_farm[packet.frame_id]
        finally:
            self.farm_lock.release()

        return response

    def send_message( self, address, message, timeout=1.0 ):
        """send message to remote xbee with given address

           returns true on success
        """
        # build packet
        packet = Transmit_Packet( address=address, message=message )

        # send packet and return response
        return self._send_and_wait( packet, timeout )

    def set_pan_id( self, pan_id, timeout=1.0 ):
        """set two byte xbee pan id from two ints

           returns true on success
        """
        # build packet
        packet = Command_Packet( "ID", *pan_id )

        # send packet and return response
        return self._send_and_wait( packet, timeout )

    def set_source_address( self, address, timeout=1.0 ):
        """set this xbee's two byte address from two ints

           returns true on success
        """
        # build packet
        packet = Command_Packet( "MY", *address )

        # send packet and return response
        return self._send_and_wait( packet, timeout )

    def _send_and_wait( self, packet, timeout=1.0 ):
        # write packet to serial port
        self.write( packet )

        # wait for response
        response = None
        try:
            response = self.get_response( packet, timeout )
        except IOError:
            return False

        # return opposite of error status
        return not response.error

    def _write_to_serial( self, packet ):
        # seal packet with frame id
        packet.seal( frame_id=self.frame_counter )

        # increment frame counter
        self.frame_counter += 1
        if self.frame_counter > 0xff:
            self.frame_counter = 1

        # place response queue in response farm
        self.farm_lock.acquire()
        try:
            if packet.frame_id in self.response_farm:
                raise IOError( "packet frame id already in response farm" )
            self.response_farm[packet.frame_id] = packet.response_queue
        finally:
            self.farm_lock.release()

        # write packet buffer to serial port
        buff_string = "".join( chr(b) for b in packet.buff )
        print "writing:", buff_string, "...",
        
        self.port.write( buff_string )
        
        print "done writing"

    def _process_data( self, bytes ):
        for b in bytes:
            #print "[%x]" % b,

            # look for delimiter
            if b == 0x7e:
                if self.count_state != 0:
                    print "unexpected start of packet!", self.read_buff
                    self.read_buff = []
                self.count_state = 1
                self.count = 0

            # look for escape chars
            elif b == 0x7d:
                self.escape_next = True

            # get count
            elif self.count_state == 1:
                if self.escape_next:
                    b = b ^ 0x20
                    self.escape_next = False
                self.count = b * 256
                self.count_state = 2
            elif self.count_state == 2:
                if self.escape_next:
                    b = b ^ 0x20
                    self.escape_next = False
                self.count += b
                self.count_state = 3

            # capture bytes up to count
            else:
                if self.escape_next:
                    b = b ^ 0x20
                    self.escape_next = False
                    
                # parse packet from data buffer when full
                if len(self.read_buff) == self.count:

                    # verify checksum
                    if (sum(self.read_buff) + b) & 0xff == 0xff:
                        self._parse_packet( self.read_buff )
                    else:
                        print "packet failed checksum!", self.read_buff
                    self.read_buff = []
                    self.count_state = 0
                    self.count = 0
                else:
                    self.read_buff.append( b )

    def _parse_packet( self, buff ):
        # determine packet type from api id
        api_id = buff[0]

        # place receive packets on read buffer
        if api_id == 0x80 or api_id == 0x81:
            packet = Receive_Packet( buff )
            self.read_queue.put( packet )

        # place response packets on appopriate queue in response farm
        elif api_id == 0x88 or api_id == 0x89:
            packet = None
            if api_id == 0x88:
                packet = Command_Response_Packet( buff )
            elif api_id == 0x89:
                packet = Transmit_Response_Packet( buff )
            self.farm_lock.acquire()
            try:
                self.response_farm[packet.frame_id].put( packet )
            finally:
                self.farm_lock.release()

        else:
            print "unknown packet type received:", api_id


        
        
