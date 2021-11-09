import os
import sys
import subprocess

class LocalGroup:
	root_group = 0
	users_group = 100

	def __init__(self, group_name: str = "users", gid: int = -1):
		self.group_name = group_name
		self.gid = gid if gid >= 0 else None

	
	def register(self):
		options: str = ""

		if self.gid != None:
			options += f"""-g {self.gid}"""

		result = subprocess.run(f"""/usr/sbin/groupadd {options} {self.group_name}""", shell = True)
		return result


	def delete(self):
		result = subprocess.run(f"""/usr/sbin/groupdel {self.group_name}""", shell = True)


	def __str__(self):
		return f"""{self.group_name} | {self.gid}"""
