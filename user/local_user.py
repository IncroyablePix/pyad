import os
import sys
import subprocess
from pyad.user.local_group import LocalGroup

class LocalUser:
	def __init__(self, user_name: str, password: str = ""):
		self.user_name = user_name
		self.password = password


	def register(self, group = -1):
		options: str = ""

		if group != -1:
			if isinstance(group, str):
				options += f"""-g {group}"""
			elif isinstance(group, int):
				options += f"""-g --gid {group}"""


		result = subprocess.run(f"""/usr/sbin/useradd {options} -p {self.password} {self.user_name}""", shell = True)
		return result


	def delete(self):
		result = subprocess.run(f"""/usr/sbin/userdel {self.user_name}""", shell = True)
		return result



	def add_to_group(self, local_group: LocalGroup):
		result = subprocess.run(f"""/usr/sbin/usermod -a -G {local_group.group_name} {self.user_name}""", shell = True)
		return result


	def __str__(self):
		return f"""{self.user_name} | {self.password}"""


