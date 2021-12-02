import os
import sys
import subprocess
from pyad.user.global_group import GlobalGroup

class GlobalUser:
	insert_file = """/tmp/user.ldif"""
	add_member_file = """/tmp/add_user.ldif"""

	def __init__(self, last_name: str, first_name: str, uid: str, user_name: str, password: str):
		self.last_name = last_name
		self.first_name = first_name
		self.uid = uid
		self.user_name = user_name
		self.password = GlobalUser.__hash_password(password)


	def register(self, gid: int = None, ou_hierarchy: list = [], ldappasswd: str = None, dc: str = "localdomain"):
		with open(GlobalUser.insert_file, """w""") as temp_file:
			ous: str = """, """.join(map(lambda ou : f"""ou={ou}""", ou_hierarchy))
			temp_file.write(f"""dn: uid={self.user_name},{ous},dc={dc}\n""")
			temp_file.write(f"""objectClass: top\n""")
			temp_file.write(f"""objectClass: inetorgperson\n""")
			temp_file.write(f"""objectClass: posixAccount\n""")
			temp_file.write(f"""cn: {self.first_name} {self.last_name}\n""")
			temp_file.write(f"""sn: {self.last_name}\n""")
			temp_file.write(f"""givenname: {self.first_name}\n""")
			temp_file.write(f"""userPassword: {self.password}\n""")
			if gid != None:
				temp_file.write(f"""gidNumber: {gid}\n""")
			temp_file.write(f"""uidNumber: {self.uid}\n""")
			temp_file.write(f"""homeDirectory: /home/{self.user_name}\n""")
			temp_file.write(f"""loginShell: /bin/bash\n""")

		self.__create_home_dir()

		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""

		result = subprocess.run(f"""/usr/bin/ldapadd {options} -D 'cn=Directory Manager,dc={dc}' -f {GlobalUser.insert_file} -x""", shell = True)
		return result

	
	def add_to_group(self, global_group: GlobalGroup, ldappasswd: str = None, dc: str = "localdomain"):
		with open(GlobalUser.add_member_file, """w""") as temp_file:
			temp_file.write(f"""dn: cn={global_group.group_name},ou={global_group.ou_name},dc={dc}\n""")
			temp_file.write(f"""changetype: modify\n""")
			temp_file.write(f"""add: memberuid\n""")
			temp_file.write(f"""memberuid: {self.user_name}\n""")

		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""

		result = subprocess.run(f"""/usr/bin/ldapadd {options} -D 'cn=Directory Manager,dc={dc}' -f {GlobalUser.add_member_file} -x""", shell = True)
		return result
	

	@staticmethod
	def __hash_password(password: str):
		result = subprocess.run(f"""/usr/sbin/slappasswd -s {password}""", stdout=subprocess.PIPE, shell = True)
		return result.stdout.decode().rstrip("""\n""")


	def __create_home_dir(self):
		subprocess.run(f"""/usr/bin/mkdir /home/{self.user_name}""", shell = True)


	def __str__(self):
		return f"""{self.first_name} {self.last_name} | {self.uid} | {self.user_name} {self.password}"""


