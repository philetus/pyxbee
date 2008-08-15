from serial import Serial
from Queue import Queue, Empty
from threading import Thread, Lock
from time import sleep
from Packet_Demon import Packet_Demon

class Xbee( Thread ):
    """library to control xbee in api mode
    """
    PACKET_DEMON_COUNT = 5

    def __init__( self, port="/dev/ttyUSB0", timeout=0.1 ):
        Thread.__init__( self )

        # open serial port
        self.port = Serial( port=port, timeout=timeout )

        # xbee ignores first thing you write to it?
        self.port.write( "X" )
        sleep( 0.3 )

        # clear serial port input buffer
        self.port.flushInput()
        sleep( 0.3 )

        self.read_queue = Queue()

        # queue of packet demon parser threads
        self.idle_packet_demons = Queue()
        for i in range( self.PACKET_DEMON_COUNT ):
            demon = Packet_Demon( name=i,
                                  idle_queue=self.idle_packet_demons,
                                  output_queue=self.read_queue )
            demon.start()
            self.idle_packet_demons.put( demon )

    def is_open( self ):
        return self.port.isOpen()

    def run( self ):
        demon = self.idle_packet_demons.get()

        # loop and read data from serial port
        while self.port:

            # if there is no data take a breather
            waiting = self.port.inWaiting()
            if waiting == 0:
                sleep( 0.1 )
            else:

                # read string from serial port
                raw = self.port.read( waiting )

                # place data up to next delimiter on current demon
                while raw:

                    # if there is no start delimiter just add whole string
                    # to current packet demon's input queue
                    if '\x7e' not in raw:
                        demon.input_queue.put( raw )
                        raw = ""

                    # otherwise put string up to next start delimiter in
                    # current demon, then a None to close stream,
                    # then get new demon
                    else:
                        delimiter_index = raw.index( '\x7e' )
                        demon.input_queue.put( raw[:delimiter_index] )
                        demon.input_queue.put( None )
                        raw = raw[delimiter_index + 1:]
                        demon = self.idle_packet_demons.get()
                        
    def read( self, timeout=1.0 ):
        """read packet from xbee
        """
        return self.read_queue.get( timeout=timeout )

