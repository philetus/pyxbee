from Write_Packet import Write_Packet

class Transmit_Packet( Write_Packet ):
    """packet to send message to remote xbee
    """

    def __init__( self, address, message ):
        Write_Packet.__init__( self, 0x01 )

        # append 2-byte address
        self.address = [ int(b) & 0xff for b in address ]
        assert len(self.address) == 2
        self.buff.extend( self.address )

        # append blank options byte
        self.buff.append( 0x00 )

        # append message
        if type(message) is str:
            self.message = [ ord(c) for c in message ]
        else:
            self.message = [ int(b) & 0xff for b in message ]
        assert len(self.message) <= 100
        self.buff.extend( self.message )

    def __repr__( self ):
        return "<" + ":".join( "%x" % b for b in self.buff ) + ">"
