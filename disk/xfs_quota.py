import os
import sys
import subprocess
import re


class XFSQuota:
	disk_file = """/etc/fstab"""
	project_file = """/etc/projects"""
	projid_file = """/etc/projid"""

	def __init__(self, partition_name: str):
		self.partition_name = partition_name

	
	def enable_quota(self):
		lines: list = []
		
		with open(XFSQuota.disk_file, """r""") as temp_file:
			for line in temp_file:
				pattern = re.compile(r"""(\/([a-zA-Z]|\-)*)+\s+(\/([a-zA-Z]|\-)*)+\s+xfs\s+((\w*\,)*\w+)\s+\d\s+\d""")
				match = pattern.match(line.rstrip())
		        
				if match and match.group(3) == self.partition_name:
					if match.group(5) == """defaults""":
						lines.append(line.replace("defaults", "defaults,grpquota,usrquota,prjquota"))
					else:
						lines.append(line)
				else:
					lines.append(line)
		            
		with open(XFSQuota.disk_file, """w""") as temp_file:
			for line in lines:
				temp_file.write(line)

		result = []
		result.append(subprocess.run(f"""/usr/bin/systemctl daemon-reload""", shell = True))
		result.append(subprocess.run(f"""/usr/bin/mount {self.partition_name} -o remount""", shell = True))

		return result


	def display(self):
		result = subprocess.run(f"""/usr/sbin/xfs_quota -x -c 'report -a -h' {self.partition_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if result.returncode == 0:
			print(result.stdout.decode("ASCII"))

	def set_user_quota(self, user_name: str, soft: int, hard: int, print_result: bool = True):
		result = subprocess.run(f"""/usr/sbin/xfs_quota -x -c 'limit bsoft={soft}m bhard={hard}m {user_name}' {self.partition_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		
		if print_result:
			if result.returncode == 0:
				print(f"""Created user quota for {user_name} (Soft: {soft}M - Hard: {hard})""")
			else:
				print(f"""Error during user quota creation: {result.stdout[0:-1].decode('ascii')}""")
		return result


	def set_group_quota(self, group_name: str, soft: int, hard: int, print_result: bool = True):
		result = subprocess.run(f"""/usr/sbin/xfs_quota -x -c 'limit -g bsoft={soft}m bhard={hard}m {group_name}' {self.partition_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

		if print_result:
			if result.returncode == 0:
				print(f"""Created group quota for {self.group_name} (Soft: {soft}M - Hard: {hard})""")
			else:
				print(f"""Error during group quota creation: {result.stdout[0:-1].decode('ascii')}""")
		return result
		
	
	def set_project_quota(self, project_name: str, hard: int, project_id: int, path: str, print_result: bool = True):
		with open(XFSQuota.project_file, """a""") as projects:
			projects.write(f"""{project_id}:{path}\n""")

		with open(XFSQuota.projid_file, """a""") as projid:
			projid.write(f"""{project_name}:{project_id}\n""")

		result = subprocess.run(f"""/usr/sbin/xfs_quota -x -c 'project -s {project_name}' {self.partition_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

		if result.returncode == 0:
			if print_result:
				print(f"""Created XFS project "{project_name}" """)
			result = subprocess.run(f"""/usr/sbin/xfs_quota -x -c 'limit -p bhard={hard}m {project_name}' {self.partition_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

			if print_result:
				if result.returncode == 0:
					print(f"""Added quota to project "{project_name}" """)
				else:
					print(f"""Error during project quota creation: {result.stdout[0:-1].decode('ascii')}""")
		elif print_result:
			print(f"""Error during XFS project creation: {result.stdout[0:-1].decode('ascii')}""")

		return result

