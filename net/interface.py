import os
import sys
import subprocess
from subprocess import PIPE
from pyad.utils.colors import TColor

class NetInterface: 
	def __init__(self, name: str = None):
		self.name = name


	def set_static_ip(self, ipv: int, ip: str, mask: int, gateway: str, dns: list = [], print_result: bool = True):	
		param = "ipv6" if ipv == 6 else "ipv4"
		
		dns_param = f"""{param}.dns "{" ".join(dns)}" """ if len(dns) > 0 else " "
		
		result = subprocess.run(f"""/usr/bin/nmcli connection modify {self.name} {param}.method manual {param}.address {ip}/{mask} {param}.gateway {gateway} {dns_param} """, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Static IP(v{ipv}) set to {ip}/{mask}.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error setting static IP: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""") 

	
	def add_static_ip(self, ipv: int, ip: str, mask: int, print_result: bool = True):
		param = "ipv6" if ipv == 6 else "ipv4"
		result = subprocess.run(f"""/usr/bin/nmcli connection modify {self.name} +{param}.address {ip}/{mask}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Static IP(v{ipv}) added: {ip}/{mask}.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error adding static IP: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""") 
	

	def remove_static_ip(self, ipv: int, ip: str, mask: int):
		param = "ipv6" if ipv == 6 else "ipv4"
		result = subprocess.run(f"""/usr/bin/nmcli connection modify {self.name} -{param}.address {ip}/{mask}""", shell = True)


	def reload(self, print_result: bool = True):
		result = subprocess.run(f"""/usr/bin/nmcli device disconnect {self.name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Disconnected device {self.name}.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error disconnecting device {self.name}: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
				
		result = subprocess.run(f"""/usr/bin/nmcli device connect {self.name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Connected device {self.name}.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error connecting device {self.name}: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")

	
	def toggle(self, toggle: bool):
		up_down = "up" if toggle else "down"
		result = subprocess.run(f"""/usr/sbin/ip link set {self.name} {up_down}""", shell = True)
	

	def enable_dhcp(self, ipv: int):
		param = "ipv6" if ipv == 6 else "ipv4"
		result = subprocess.run(f"""/usr/bin/nmcli connection modify {self.name} {param}.method auto""", shell = True)


	def remove_current_ip(self, ip: str, mask: int):
		result = subprocess.run(f"""/usr/sbin/ip addr del {ip}/{mask} dev {self.name}""", shell = True)


	def add_current_ip(self, ip: str, mask: int):
		result = subprocess.run(f"""/usr/sbin/ip addr add {ip}/{mask} dev {self.name}""", shell = True)


	@staticmethod
	def __cut_interface(text: str):
		return text.split(" ")[0]


	@staticmethod
	def all_interfaces() -> list:
		result = ""
		result += bytes.decode(subprocess.run(f"""/sbin/ip -6 -o a | cut -d ' ' -f 2,7 | cut -d '/' -f 1""", shell = True, stdout = PIPE, stderr = PIPE).stdout)
		result += bytes.decode(subprocess.run(f"""/sbin/ip -4 -o a | cut -d ' ' -f 2,7 | cut -d '/' -f 1""", shell = True, stdout = PIPE, stderr = PIPE).stdout)

		interfaces = list(filter(lambda e: len(e) > 0, dict.fromkeys(map(NetInterface.__cut_interface, result.split("\n")))))
		
		return interfaces
		
		
