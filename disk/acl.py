import os
import re
import sys
import subprocess
from os.path import exists
from pyad.utils.colors import TColor

class ACL:
	def __init__(self, p_type: str = "user", principal: str = "", read: bool = True, write: bool = True, execute: bool = True, default: bool = True):
		self.p_type = "u"
		
		if p_type == "user" or p_type == "u":
			self.p_type = "u"
		elif p_type == "group" or p_type == "g":
			self.p_type = "g"
		else:
			self.p_type = "o"
			
		self.principal = principal
		self.read = read
		self.write = write
		self.execute = execute
		self.default = default
		
		
	def perm(self):
		permission = ""
		
		permission += "r" if self.read else "-"
		permission += "w" if self.write else "-"
		permission += "x" if self.execute else "-"
		return permission
		
	
	def get_line(self):
		return f"""{"d:" if self.default else ""}{self.p_type}:{self.principal}:{self.perm()}"""
		

class ACLFile:
	def __init__(self, path: str = None, pre_process: bool = False):
		if not exists(path):
			raise Exception(f""""{path}" is invalid""")

		self.path = path

		self.owner_name = None
		self.owner_group_name = None

		self.owner = None
		self.group = None
		self.other = None

		self.groups = {}
		self.inherited = {}
		self.users = {}
		
		self.acls = []

		if pre_process:
			self.get_acls()
			
			
	def add_acls(self, acls = None):
		if type(acls) is list:
			for acl in acls:
				self.add_acls(acl)
		elif type(acls) is ACL:
			if acls not in self.acls:
				self.acls.append(acls)
				

	def set_acls(self, print_result: bool = True):
		to_add = " ".join(map(lambda a: f"""-m {a.get_line()}""", self.acls))
		result = subprocess.run(f"""/usr/bin/setfacl {to_add} {self.path}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}ACLs added for file {self.path}{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Error adding ACLs for file {self.path}: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
	
	
	def get_acls(self):
		result = subprocess.run(f"""/usr/bin/getfacl {path}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if result.returncode != 0:		
			raise Exception(f"""Error while getting ACLs for {path}""")
	
		### Regexes
		owner_regex = re.compile(r"""#\s*owner:\s*([a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}))""")
		owner_group_regex = re.compile(r"""#\s*group:\s*([a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}))""")

		user_regex = re.compile(r"""user:([a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}))?:([r|\-][w|\-][x|\-])""")
		group_regex = re.compile(r"""group:([a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}))?:([r|\-][w|\-][x|\-])""")
		other_regex = re.compile(r"""other:([a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}))?:([r|\-][w|\-][x|\-])""")
		default_regex = re.compile(r"""default:([a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}))?:([a-z_]([a-z0-9_-]{0,31}|[a-z0-9_-]{0,30}))?:([r|\-][w|\-][x|\-])""")
		###

		lines = result.stdout.decode("ASCII").split("\n")
		for line in lines:
			if not line:
				break

			# Owner name
			if self.owner_name == None:
				mo = owner_regex.search(line)
				if mo == None:
					continue

				groups = mo.groups()
				if len(groups) > 0:
					self.owner_name = groups[0]
					continue

			# Owner group name
			if self.owner_group_name == None:
				if mo != None:
					mo = owner_group_regex.search(line)
					groups = mo.groups()
					if len(groups) > 0:
						self.owner_group_name = groups[0]

			# Others
			if self.other == None:
				mo = other_regex.search(line)
				if mo != None:
					groups = mo.groups()
					if len(groups) > 0:
						self.other = groups[2]
					continue


			# Inherited
			ir = default_regex.search(line)
			if ir != None:
				groups = ir.groups()
				if len(groups) > 0:
					if groups[1] == "user":
						pass
					elif groups[1] == "group":
						pass
					elif groups[1] == "other":
						pass
				continue


			# Users		
			ur = user_regex.search(line)
			if ur != None:
				groups = ur.groups()
				if len(groups) > 0:
					if groups[1] != None and len(groups[1]) > 0: # Other user
						self.users[groups[1]] = groups[2]
					else: # Owner user
						self.owner = groups[2]
					continue

			# Groups
			gr = group_regex.search(line)
			if gr != None:
				groups_g = gr.groups()
				if len(groups) > 0:
					if groups[1] != None and len(groups[1]) > 0: # Other group
						self.groups[groups[1]] = groups[2]
					else: # Owner group
						self.group = groups[2]
					continue




