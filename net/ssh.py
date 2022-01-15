import os
import sys
import subprocess
from subprocess import PIPE
from pyad.utils.colors import TColor

class SSHKey: 
	algorithms = ["ed25519", "rsa"]
	
	@staticmethod
	def create(name: str = "my-ssh", algorithm: str = "ed25519", password: str = "", ) -> SSHKey:
		if algorithm not in SSHKey.algorithms:
			algorithm = "ed25519"
			
		result = subprocess.run(f"""/usr/bin/ssh-keygen -t {algorithm} -f "$HOME/.ssh/{name}" -P "{password}" """, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Created SSH Key "{name}".{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error creating SSH Key: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
		
		return SSHKey(name = name)
		

	def __init__(self, name: str = None, path: str = "$HOME/.ssh"):
		self.name = name
		self.key_path = f"""{path}/{name}"""


	def add_for_authentication(self, user_name: str = "", password: str = "", server: str = None):
		if not server:
			print(f"""{TColor.FAIL}Error during SSH Key export: {TColor.WARNING}Unknown server "{server}".{TColor.ENDC} """)
			return
			
		if not user_name:
			print(f"""{TColor.FAIL}Error during SSH Key export: {TColor.WARNING}No user specified.{TColor.ENDC} """)
			return
			
		result = subprocess.run(f"""/usr/bin/ssh-copy-id -i {self.key_path}.pub {user_name}@{server}""", shell = True, input = f"""{password}\n""", stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Exported SSH Key "{self.key_path}".{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error during SSH Key export: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
				
				
