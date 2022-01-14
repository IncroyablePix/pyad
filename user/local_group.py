import os
import sys
import subprocess

class LocalGroup:
	root_group = 0
	users_group = 100

	def __init__(self, group_name: str = "users", gid: int = -1):
		self.group_name = group_name
		self.gid = gid if gid >= 0 else None


	def exists(self):
		result = subprocess.run(f"""/usr/bin/cat /etc/group | grep {self.group_name}""", shell = True, stdout = subprocess.PIPE).stdout[0:-1].decode('ascii')

		if len(result) > 0:
			lines = result.split("\n")
			for line in lines:
				if line.split(":")[0] == self.group_name:
					return True

		return False

	
	def register(self, print_result: bool = True):
		options: str = ""

		if self.gid != None:
			options += f"""-g {self.gid}"""

		result = subprocess.run(f"""/usr/sbin/groupadd {options} {self.group_name}""", shell = True,  stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""Created local group {self.group_name}""")
			else:
				print(f"""Error local group creation: {result.stdout[0:-1].decode('ascii')}""")
		return result


	def delete(self):
		result = subprocess.run(f"""/usr/sbin/groupdel {self.group_name}""", shell = True)


	def __str__(self):
		return f"""{self.group_name} | {self.gid}"""
