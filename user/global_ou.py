import os
import sys
import subprocess

class GlobalOU:
	insert_file = """/tmp/ou.ldif"""

	def __init__(self, ou_name: str, master_ou_name: str, description: str):
		self.ou_name = ou_name
		self.master_ou_name = master_ou_name
		self.description = description


	def register(self, ldappasswd: str = None):
		with open(GlobalOU.insert_file, """w""") as temp_file:
			temp_file.write(f"""dn: ou={self.ou_name}, ou={self.master_ou_name}, dc=localdomain\n""")
			temp_file.write(f"""ou: {self.ou_name}\n""")
			temp_file.write(f"""description: {self.description}\n""")
			temp_file.write(f"""objectClass: top\n""")
			temp_file.write(f"""objectClass: organizationalUnit\n""")

		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""

		result = subprocess.run(f"""/usr/bin/ldapadd {options} -D 'cn=Directory Manager,dc=localdomain' -f {GlobalOU.insert_file} -x""", shell = True)
		return result


	def __str__(self):
		return f"""{self.master_ou_name}::{self.ou_name} : {self.description}s"""

