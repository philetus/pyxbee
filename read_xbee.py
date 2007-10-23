from Xbee import Xbee

print "starting xbee"
x = Xbee()
x.start()
print "xbee started"

#print "setting pan id", x.set_pan_id( [0x00, 0x07] )
#print "setting address", x.set_source_address( [0x00, 0x01] )


while True:
    print x.read( timeout=None ), "\n\n"
