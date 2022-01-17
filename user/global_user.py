import os
import sys
import subprocess
from pyad.user.global_group import GlobalGroup
from pyad.user.local_group import LocalGroup
from pyad.user.user import User
from pyad.utils.colors import TColor

class GlobalUser(User):
	insert_file = """/tmp/user.ldif"""
	add_member_file = """/tmp/add_user.ldif"""

	def __init__(self, last_name: str, first_name: str, uid: str, user_name: str, password: str):
		super(GlobalUser, self).__init__(user_name = user_name, password = password)
		self.last_name = last_name
		self.first_name = first_name
		self.uid = uid
		self.hashed_password = GlobalUser.__hash_password(password)


	def register(self, gid: int = None, ou_hierarchy: list = [], ldappasswd: str = None, dc: str = "localdomain", home_base: str = "/home", samba_user: bool = True, apache_dir: str = "public_html", print_result: bool = True):
		with open(GlobalUser.insert_file, """w""") as temp_file:
			ous: str = """, """.join(map(lambda ou : f"""ou={ou}""", ou_hierarchy))
			temp_file.write(f"""dn: uid={self.user_name},{ous},dc={dc}\n""")
			temp_file.write(f"""objectClass: top\n""")
			temp_file.write(f"""objectClass: inetorgperson\n""")
			temp_file.write(f"""objectClass: posixAccount\n""")
			temp_file.write(f"""cn: {self.first_name} {self.last_name}\n""")
			temp_file.write(f"""sn: {self.last_name}\n""")
			temp_file.write(f"""givenname: {self.first_name}\n""")
			temp_file.write(f"""userPassword: {self.hashed_password}\n""")
			if gid != None:
				temp_file.write(f"""gidNumber: {gid}\n""")
			temp_file.write(f"""uidNumber: {self.uid}\n""")
			temp_file.write(f"""homeDirectory: /home/{self.user_name}\n""")
			temp_file.write(f"""loginShell: /bin/bash\n""")

		self.__create_home_dir(home_base = home_base, gid = gid)

		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""

		result = subprocess.run(f"""/usr/bin/ldapadd {options} -D 'cn=Directory Manager,dc={dc}' -f {GlobalUser.insert_file} -x""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Global user {self.user_name} created.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error in global user creation: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")

		if samba_user:
			self.toggle_samba(toggle = True)
			
		if apache_dir != None:
			self.add_apache_dir(directory = apache_dir, user_home = home_base)

		return result			
			
			
	def delete(self, samba_user: bool = True, ou_hierarchy: list = [], ldappasswd: str = None, dc: str = "localdomain", print_result: bool = True):

		if samba_user:
			self.toggle_samba(toggle = False)
			
		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""
			
		result = subprocess.run(f"""/usr/bin/ldapdelete -x "uid={self.user_name},{ous},dc={dc}" {options}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Global user {self.user_name} deleted.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error deleting global user: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
	

		return result
		
			
	def add_to_global_group(self, global_group: GlobalGroup, ldappasswd: str = None, dc: str = "localdomain"):
		with open(GlobalUser.add_member_file, """w""") as temp_file:
			temp_file.write(f"""dn: cn={global_group.group_name},ou={global_group.ou_name},dc={dc}\n""")
			temp_file.write(f"""changetype: modify\n""")
			temp_file.write(f"""add: memberuid\n""")
			temp_file.write(f"""memberuid: {self.user_name}\n""")

		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""

		result = subprocess.run(f"""/usr/bin/ldapadd {options} -D 'cn=Directory Manager,dc={dc}' -f {GlobalUser.add_member_file} -x""", shell = True,  stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		return result
	

	@staticmethod
	def __hash_password(password: str):
		result = subprocess.run(f"""/usr/sbin/slappasswd -s {password}""", stdout=subprocess.PIPE, shell = True)
		return result.stdout.decode().rstrip("""\n""")


	def __create_home_dir(self, home_base: str = "/home", gid: int = None, print_result: bool = True):
		'''result = subprocess.run(f"""/usr/bin/mkdir {home_base}/{self.user_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Home directory created{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Failed to create directory {home_base}/{self.user_name}: {TColor.WARNING} {result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")'''
		try:	
			os.makedirs(f"""{home_base}/{self.user_name}""")
			print(f"""{TColor.OKGREEN}Home directory created{TColor.ENDC}""")
		except FileExistsError:
			print(f"""{TColor.FAIL}Failed to create directory {home_base}/{self.user_name}: {TColor.WARNING} Already exists{TColor.ENDC}""")
			
		os.chown(f"""{home_base}/{self.user_name}""", self.uid, gid)
		os.chmod(f"""{home_base}/{self.user_name}""", 0o751)


	def __str__(self):
		return f"""{self.first_name} {self.last_name} | {self.uid} | {self.user_name} {self.password}"""


