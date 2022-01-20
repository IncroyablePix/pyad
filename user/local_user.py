import os
import sys
import subprocess
from pyad.user.local_group import LocalGroup
from pyad.utils.colors import TColor
from pyad.user.user import User

class LocalUser(User):
	def __init__(self, user_name: str, password: str = "", full_name: str = ""):
		super(LocalUser, self).__init__(user_name = user_name, password = password)
		self.full_name = full_name


	def register(self, group = -1, samba_user: bool = True, mail: str = None, apache_dir: str = "public_html", print_result: bool = True):
		options: str = ""

		if group != -1:
			if isinstance(group, str):
				options += f"""-g {group}"""
			elif isinstance(group, int):
				options += f"""--gid {group}"""

		if len(self.full_name) > 0:
			options += f"""-c {self.full_name}"""

		result = subprocess.run(f"""/usr/sbin/useradd {options} -p $(perl -e 'print crypt($ARGV[0], "password")' '{self.password}') {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Local user {self.user_name} created.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error in local user creation: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")

		os.chmod(f"""/home/{self.user_name}""", 0o711)
		
		if samba_user:
			self.toggle_samba(toggle = True)
			
		if apache_dir != None:
			self.add_apache_dir(directory = apache_dir, user_home = "/home")
			
		if mail != None:
			self.add_mail_address(mail = mail)
		
		return result
			
			
	def delete(self, samba_user: bool = True, print_result: bool = True):
		if samba_user:
			self.toggle_samba(toggle = False)
			
		result = subprocess.run(f"""/usr/sbin/userdel {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Local user {self.user_name} deleted.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error deleting local user: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")

		return result


	def __str__(self):
		return f"""{self.user_name} | {self.password}"""


