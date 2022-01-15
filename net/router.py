import os
import sys
import subprocess
from subprocess import PIPE
from pyad.utils.colors import TColor

__IP_FORWARD_FILE = """/etc/sysctl.d/10-ipforward.conf"""

def toggle_router_mode(network_ip: str, network_mask: int, toggle: bool = True, conf_file: str = __IP_FORWARD_FILE, print_result: bool = True):
	if toggle:
		with open(conf_file, """w+""") as temp_file:
			temp_file.write("""# Enabling IP Forwarding\n""")
			temp_file.write("""net.ipv4.ip_forward=1""")
	

		if print_result:
			print(f"""{TColor.OKGREEN}Enabled IP Forwarding...{TColor.ENDC}""")
	
		
		# NFT 
		result = subprocess.run(f"""/usr/sbin/nft add table ip nat""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if result.returncode != 0:
			if print_result:
				print(f"""{TColor.FAIL}Failed to add NAT table into nft: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")		
				return
				
		
		result = subprocess.run("""/usr/sbin/nft add chain nat postrouting { type nat hook postrouting priority 100 \\; }""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if result.returncode != 0:
			if print_result:
				print(f"""{TColor.FAIL}Failed to add postrouting into nft: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")		
				return
		
		
		result = subprocess.run(f"""/usr/sbin/nft add rule nat postrouting ip saddr {network_ip}/{network_mask} masquerade""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if result.returncode != 0:
			if print_result:
				print(f"""{TColor.FAIL}Failed to add NAT rule into nft: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")		
				return
		
		
		result = subprocess.run(f"""/usr/sbin/nft list ruleset > /etc/nftables/default.nft""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if result.returncode != 0:
			if print_result:
				print(f"""{TColor.FAIL}Failed to save nft rules: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")		
				return
				
		if print_result:
			print(f"""{TColor.OKGREEN}Added NFT entries.{TColor.ENDC}""")
			print(f"""{TColor.OKGREEN}Enabled router mode.{TColor.ENDC}""")
				
	else:
		result = subprocess.run(f"""/usr/bin/rm {conf_file}""")
		
		if print_result:
			print(f"""{TColor.OKGREEN}Disabled router mode.{TColor.ENDC}""")
		
