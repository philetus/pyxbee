from Write_Packet import Write_Packet

class Command_Packet( Write_Packet ):
    """packet to send a command to xbee chip
    """

    def __init__( self, command, *args ):
        Write_Packet.__init__( self, api_id=0x08 )

        # two-character command code
        self.command = str(command)
        assert len(self.command) == 2
        self.buff.extend( (ord(c) for c in self.command) )

        # command arguments
        self.args = [ int(b) & 0xff for b in args ]
        self.buff.extend( self.args )
