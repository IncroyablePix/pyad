import os
import sys
import subprocess
import pwd
import grp
from pyad.disk.acl import ACL, ACLFile
from pyad.user.local_group import LocalGroup
from pyad.utils.colors import TColor
from abc import ABC, abstractmethod


class User(ABC):
	def __init__(self, user_name: str = "", password: str = ""):
		self.user_name = user_name
		self.password = password
		
	def toggle_ftp_navigate(self, toggle: bool = True, path: str = "/etc/vsftpd/chroot_list", print_result: bool = True):
		if not os.path.exists(path):
			print(f"""{TColor.FAIL}Error adding user to FTP navigation: {TColor.WARNING}List '{path}' does not exist.{TColor.ENDC}""")
			return
			
		with open(path, "a") as f: 
			f.write(f"""{self.user_name}\n""")
			
		print(f"""{TColor.OKGREEN}User successfully added to chroot list{TColor.ENDC}""")
	
	def add_to_ftp_whitelist(self, path: str = "/etc/vsftpd/user_list", print_result: bool = True):
		if not os.path.exists(path):
			print(f"""{TColor.FAIL}Error adding user to FTP whitelist: {TColor.WARNING}List '{path}' does not exist.{TColor.ENDC}""")
			return
			
		with open(path, "a") as f: 
			f.write(f"""{self.user_name}\n""")
			
		print(f"""{TColor.OKGREEN}User successfully added to FTP whitelist.{TColor.ENDC}""")
		
	
	def toggle_apache(self, passwd_file: str = None, toggle: bool = True, print_result: bool = True):
		result = None
		if passwd_file != None:
			if toggle: # Add user
				if os.path.exists(passwd_file):
					result = subprocess.run(f"""/usr/bin/htpasswd -b {passwd_file} {self.user_name} {self.password}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
				else:
					result = subprocess.run(f"""/usr/bin/htpasswd -b -c {passwd_file} {self.user_name} {self.password}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			
				if print_result:
					if result.returncode == 0:
						print(f"""{TColor.OKGREEN}Apache user {self.user_name} created to '{passwd_file}'.{TColor.ENDC}""")
					else:
						print(f"""{TColor.FAIL}Error creating apache user: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
			else: # Delete user
				result = subprocess.run(f"""/usr/bin/htpasswd -D {passwd_file} {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

				if print_result:
					if result.returncode == 0:
						print(f"""{TColor.OKGREEN}Apache user {self.user_name} deleted from '{passwd_file}'.{TColor.ENDC}""")
					else:
						print(f"""{TColor.FAIL}Error deleting apache user: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
		else:
			print(f"""{TColor.FAIL}Error in apache user edition: {TColor.WARNING}Invalid file path '{passwd_file}'{TColor.ENDC}""")
			
		
	def add_apache_dir(self, user_home: str = None, directory: str = None, print_result: bool = True):
		
		if user_home != None and directory != None:
			web_dir = f"""{user_home}/{self.user_name}/{directory}"""
			try:
				os.makedirs(web_dir, 0o755)
			except:
				os.chmod(web_dir, 0o755)
			
			acl_file = ACLFile(path = web_dir)
			acl_file.add_acls(acls = [ACL(p_type = "user", principal = "apache", read = True, write = False, execute = True, default = True), ACL(p_type = "group", principal = "apache", read = True, write = False, execute = True, default = True)])
			acl_file.set_acls()

			result = subprocess.run(f"""/usr/bin/chown {self.user_name}:apache {web_dir}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

			if print_result:
				print(f"""{TColor.OKGREEN}Added apache directory "{directory}" for {self.user_name}.{TColor.ENDC}""")
		

	def toggle_samba(self, toggle: bool = True, print_result: bool = True):
		if toggle: # Samba add
			passwd = f"\"{self.password}\""
			result = subprocess.run(f"""{"{"} echo \"{self.password}\"; echo \"{self.password}\"; {"}"} | /usr/bin/smbpasswd -a {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			if print_result:
				if result.returncode == 0:
					print(f"""{TColor.OKGREEN}Samba user {self.user_name} created.{TColor.ENDC}""")
				else:
					print(f"""{TColor.FAIL}Error in samba user creation: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
 
		else: # Samba deletion
			result = subprocess.run(f"""/usr/bin/smbpasswd -x {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			if print_result:
				if result.returncode == 0:
					print(f"""{TColor.OKGREEN}Samba user {self.user_name} deleted.{TColor.ENDC}""")
				else:
					print(f"""{TColor.FAIL}Error deleting samba user: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
					

	def add_to_group(self, local_group: LocalGroup, print_result: bool = True):
		result = subprocess.run(f"""/usr/sbin/usermod -a -G {local_group.group_name} {self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Global user {self.user_name} added to local group {local_group.group_name}{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error adding global user to local group: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
		return result
