class Receive_Packet():
    """packet of data received from remote xbee
    """

    def __init__( self, buff ):
        """init takes raw array of ints tokenized by read demon

           parses address and message from raw data
        """
        # parse address
        if buff[0] == 0x80:
            self.address = buff[1:9]
            buff = buff[9:]
        elif buff[0] == 0x81:
            self.address = buff[1:3]
            buff = buff[3:]
        else:
            raise ValueError( "inappropriate code for receive packet: %#04x"
                              % buff[0] )

        # parse signal strength
        self.signal_strength = buff.pop(0)

        # parse options
        options = buff.pop(0)
        self.address_broadcast = bool( options & 2 )
        self.pan_broadcast = bool( options & 4 )

        # parse data
        self.data = list( buff )

    def __repr__( self ):
        string = "<receive_packet "
        string += "address='%s'>" % ".".join( str(i) for i in self.address )
        string += ":".join( "%x" % i for i in self.data )
        string += "</receive_packet>"
        return string
        
