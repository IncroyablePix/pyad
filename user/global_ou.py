import os
import sys
import subprocess

class GlobalOU:
	insert_file = """/tmp/ou.ldif"""

	def __init__(self, ou_name: str, ou_hierarchy: list = ["""People"""], description: str = ""):
		self.ou_name = ou_name
		self.ou_hierarchy = ou_hierarchy
		self.description = description


	def register(self, ldappasswd: str = None, dc: str = "localdomain"):
		with open(GlobalOU.insert_file, """w""") as temp_file:
			ous: str = """, """.join(map(lambda ou : f"""ou={ou}""", self.ou_hierarchy))
			temp_file.write(f"""dn: ou={self.ou_name}, {ous}, dc={dc}\n""")
			temp_file.write(f"""ou: {self.ou_name}\n""")
			temp_file.write(f"""description: {self.description}\n""")
			temp_file.write(f"""objectClass: top\n""")
			temp_file.write(f"""objectClass: organizationalUnit\n""")

		options: str = ""
		if ldappasswd != None:
			options += f"""-w {ldappasswd}"""

		result = subprocess.run(f"""/usr/bin/ldapadd {options} -D 'cn=Directory Manager,dc={dc}' -f {GlobalOU.insert_file} -x""", shell = True)
		return result


	def __str__(self):
		return f"""{self.master_ou_name}::{self.ou_name} : {self.description}s"""

