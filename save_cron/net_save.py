import os
import sys
import subprocess

# TODO : Being able to export commands to .sh files for cron/at

class SCPManager:
	def __init__(self, dest_addr: str = "", dest_user: str = ""):
		self.dest_addr = dest_addr
		self.dest_user = dest_user


	def send_cmd(self, to_copy: str = None, dest_path: str = None):
		return f"""/usr/bin/scp {to_copy} {self.dest_user}@{self.dest_addr}:{dest_path}"""


	def send(self, to_copy: str = None, dest_path: str = None):
		result = subprocess.run(self.send_cmd(to_copy = to_copy, dest_path = dest_path), shell = True)
		return result


	def get_cmd(self, to_ask: str = None, dest_path: str = None):
		destination: str = "./" if dest_path == None else dest_path
		return f"""/usr/bin/scp {self.dest_user}@{self.dest_addr}:{to_ask} {destination}"""

	
	def ask(self, to_ask: str = None, dest_path: str = None):
		result = subprocess.run(self.get_cmd(to_ask, dest_path), shell = True)
		return result


class RSyncManager:
	def __init__(self, dest_addr: str = "", dest_user: str = ""):
		self.dest_addr = dest_addr
		self.dest_user = dest_user


	def synchronize_cmd(self, to_synchronize: str = "", dest_path: str = ""):
		return f"""/usr/bin/rsync -avz {to_synchronize} {self.dest_user}@{self.dest_addr}:{dest_path} -e ssh"""

	
	def synchronize(self, to_synchronize: str = "", dest_path: str = ""):
		result = subprocess.run(self.synchronize_cmd(to_synchronize = to_synchronize, dest_path = dest_path), shell = True)
		return result

		
