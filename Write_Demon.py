from threading import Thread

class Write_Demon( Thread ):

    def __init__( self, queue, port, port_lock ):
        Thread.__init__( self )
        pass

    def run( self ):
        pass
