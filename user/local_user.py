import os
import sys
import subprocess
from pyad.user.local_group import LocalGroup

class LocalUser:
	def __init__(self, user_name: str, password: str = ""):
		self.user_name = user_name
		self.password = password


	def register(self, group = -1, print_result: bool = True):
		options: str = ""

		if group != -1:
			if isinstance(group, str):
				options += f"""-g {group}"""
			elif isinstance(group, int):
				options += f"""--gid {group}"""

		# result = subprocess.run(f"""/usr/sbin/useradd {options} -p {self.password} {self.user_name}""", shell = True)
		result = subprocess.run(f"""/usr/sbin/useradd {options} -p $(perl -e 'print crypt($ARGV[0], "password")' '{self.password}') {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""Local user {self.user_name} created.""")
			else:
				print(f"""Error in local user creation: {result.stdout[0:-1].decode('ascii')}""")
		
		return result


	def delete(self, print_result: bool = True):
		result = subprocess.run(f"""/usr/sbin/userdel {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""Local user {self.user_name} deleted.""")
			else
				print(f"""Error deleting local user: {result.stdout0:-1].decode('ascii')}""")

		return result


	def add_to_group(self, local_group: LocalGroup, print_result: bool = True):
		result = subprocess.run(f"""/usr/sbin/usermod -a -G {local_group.group_name} {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""Local user {self.user_name} added to local group {local_group.group_name}""")
			else:
				print(f"""Error adding local user to local group: {result.stdout[0:-1].decode('ascii')}""")
		return result


	def __str__(self):
		return f"""{self.user_name} | {self.password}"""


