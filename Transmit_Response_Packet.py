class Transmit_Response_Packet():
    """packet of data received to report transmit success or failure
    """

    def __init__( self, buff ):
        """init takes raw array of ints tokenized by read demon
        """
        # verify api id
        api_id = buff.pop(0)
        if api_id != 0x89:
            raise ValueError( "wrong code for transmit response packet: %#04x"
                              % api_id )

        # parse frame id
        self.frame_id = buff.pop(0)

        # parse status
        self.status = buff[0]
        self.error = bool( self.status )

