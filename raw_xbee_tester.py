from pyxbee.Xbee import Xbee
from serial import SerialException

xbee = None

try:
  xbee = Xbee( port="/dev/ttyUSB0", timeout=0.1 )
except SerialException:
  print "ERROR: Unable to find USB base station; exiting."
  from sys import exit
  exit( -1 )

xbee.start()

while xbee.is_open():
    #print "reading from", str(xbee)

    # block waiting for packet
    packet = xbee.read( timeout=None )

    print "%s: %s\n" % (str(packet.address), packet.data)
    #print "*",
