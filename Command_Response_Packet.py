class Command_Response_Packet():
    """packet of data received to report command success or failure
    """

    def __init__( self, buff ):
        """init takes raw array of ints tokenized by read demon
        """
        # verify api id
        api_id = buff.pop(0)
        if api_id != 0x88:
            raise ValueError( "wrong code for command response packet: %#04x"
                              % api_id )

        # parse frame id
        self.frame_id = buff.pop(0)

        # parse at command
        self.at_command = chr(buff.pop(0)) + chr(buff.pop(0))

        # parse status
        self.error = bool(buff.pop(0))

        # parse value of requested register
        self.value = list( buff )
        
