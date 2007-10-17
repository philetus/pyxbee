from serial import Serial
from Queue import Queue
from threading import Lock

from Read_Demon import Read_Demon
from Write_Demon import Write_Demon

class Xbee():
    """library to control xbee in api mode
    """

    def __init__( self, port="/dev/ttyUSB0", timeout=0.1 ):

        # open serial port
        self.port = Serial( port=port, timeout=timeout )
        self.port_lock = Lock() # lock to protect port access

        # start read demon
        self.read_queue = Queue()
        self.read_demon = Read_Demon( queue=self.read_queue,
                                      port=self.port,
                                      port_lock=self.port_lock )
        self.read_demon.start()

        # start write demon
        self.write_queue = Queue()
        self.write_demon = Write_Demon( queue=self.write_queue,
                                        port=self.port,
                                        port_lock=self.port_lock )
        self.write_demon.start()

    def read( self, timeout=1 ):
        """read packet from xbee
        """
        return self.read_queue.get( timeout=timeout )

    def write( self, packet ):
        """write packet to xbee
        """
        self.write_queue.put( packet )
