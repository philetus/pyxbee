from Queue import Queue

class Write_Packet():
    """superclass for packets to be written to xbee
    """

    def __init__( self, api_id ):
        self.api_id = int( api_id )
        self.frame_id = None
        self.buff = [ self.api_id, 0x00 ]
        self.response_queue = Queue()
        self.sealed = False

    def seal( self, frame_id ):
        """prepare packet to be transmitted
        """
        if self.sealed:
            self.buff = self.buff[3:-1]
        self.sealed = True
        
        # set frame id
        self.frame_id = int( frame_id )
        self.buff[1] = self.frame_id

        # calculate length
        length = len(self.buff)
        assert length < 256

        # calculate checksum
        checksum = 0xff - (sum(self.buff) & 0xff)

        # add length and checksum to buffer
        self.buff[0:0] = [ 0x00, length ]
        self.buff.append( checksum )

        # escape buffer
        for i in range( len(self.buff) ):
            if( self.buff[i] == 0x7e or self.buff[i] == 0x7d
                or self.buff[i] == 0x11 or self.buff[i] == 0x13 ):
                self.buff[i] = self.buff[i] ^ 0x20
                self.buff.insert( i, 0x7d )

        # add delimiter to beginning
        self.buff.insert( 0, 0x7e )
    
