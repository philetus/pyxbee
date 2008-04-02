class Receive_Packet():
    """packet of data received from remote xbee
    """

    def __init__( self, buff ):
        """init takes raw array of ints tokenized by read demon

           parses address and message from raw data
        """
        # parse address
        api_id = ord( buff[0] )
        if api_id == 0x80:
            self.address = tuple( ord(c) for c in buff[1:9] )
            buff = buff[9:]
        elif api_id == 0x81:
            self.address = tuple( ord(c) for c in buff[1:3] )
            buff = buff[3:]
        else:
            raise ValueError( "inappropriate code for receive packet: %#04x"
                              % api_id )

        # parse signal strength
        self.signal_strength = ord( buff[0] )

        # parse options
        options = ord( buff[1] )
        self.address_broadcast = bool( options & 2 )
        self.pan_broadcast = bool( options & 4 )

        # parse data
        self.data = buff[2:]

    def __repr__( self ):
        string = "<receive_packet "
        string += "address='%s'>" % ".".join( str(i) for i in self.address )
        string += self.data
        string += "</receive_packet>"
        return string
        
