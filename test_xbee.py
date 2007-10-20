from Xbee import Xbee
from Command_Packet import Command_Packet
from Transmit_Packet import Transmit_Packet

print "starting xbee"

x = Xbee()
x.start()

print "testing command packet"
command_packet = Command_Packet( "ID", 0x00, 0x07 )
x.write( command_packet )
command_response = x.get_response( command_packet )
print "response:", not command_response.error
print "done testing command packet"

print "testing transmit packet"
transmit_packet = Transmit_Packet( [0x00, 0x60], "hi mom" )
x.write( transmit_packet )
transmit_response = x.get_response( transmit_packet )
print "response:", not transmit_response.error
print "done testing transmit packet"
