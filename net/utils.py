import socket
import struct

def bits_to_mask(bits: int):
	net_bits = 24
	host_bits = 32 - int(net_bits)
	netmask = socket.inet_ntoa(struct.pack('!I', (1 << 32) - (1 << host_bits)))
	
	return netmask
