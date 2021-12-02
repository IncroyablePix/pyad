import os
import sys
import subprocess

class GlobalGroup:
	insert_file = """/tmp/group.ldif"""

	def __init__(self, group_name: str, ou_name: str, description: str):
		self.group_name = group_name
		self.ou_name = ou_name
		self.description = description


	def register(self, gid: int = None, ldappasswd: str = None, dc: str = "localdomain"):
		with open(GlobalGroup.insert_file, """w""") as temp_file:
			temp_file.write(f"""dn: cn={self.group_name},ou={self.ou_name},dc={dc}\n""")
			temp_file.write(f"""description: {self.description}\n""")
			temp_file.write(f"""objectClass: top\n""")
			temp_file.write(f"""objectClass: posixGroup\n""")
			temp_file.write(f"""gidNumber: {gid}\n""")

		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""

		result = subprocess.run(f"""/usr/bin/ldapadd {options} -D 'cn=Directory Manager,dc={dc}' -f {GlobalGroup.insert_file} -x""", shell = True)
		return result


	def __str__(self):
		return f"""{self.ou_name} > {self.group_name}"""


