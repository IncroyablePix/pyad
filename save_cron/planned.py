import os
import sys
import subprocess
import datetime
import uuid
import stat

'''TODO: Pour  des  raisons  de  sécurité,  il  est  possible  de  limiter  les  utilisateurs  autorisés  à  exécuter  ces 
commandes. Par défaut, tous les utilisateurs peuvent programmer des tâches ponctuelles ou 
répétitives sur les systèmes RHEL 8. Il est possible de limiter les utilisateurs en ajoutant des éléments 
dans /etc/cron.allow, /etc/cron.deny, /etc/at.allow ou /etc/at.deny. Pour plus 
d’information, référez-vous aux pages de manuel de ces commandes.'''

class RepeatTask:
	dest_dir: str = f"""/var/pyad/jobs/cron"""

	def __init__(self, name: str = None):
		self.time = ""

		if not os.path.isdir(RepeatTask.dest_dir):
			os.makedirs(RepeatTask.dest_dir, mode=0o700)

		if name != None:
			split_tup = os.path.splitext(name)
		
			file_name = split_tup[0]
			file_extension = split_tup[1]

			if len(file_extension) == 0:
				name = name + ".sh"

		self.job_file = name if name != None else f"""{uuid.uuid4()}.sh"""

		self.minute = "*"
		self.hour = "*"
		self.day = "*"
		self.month = "*"
		self.day_of_week = "*"


	def set_time(self, minute: str = None, hour: str = None, day: str = None, month: str = None, day_of_week = None):
		if minute != None:
			self.minute = minute
		
		if hour != None:
			self.hour = hour
		
		if day != None:
			self.day = day
		
		if month != None:
			self.month = month

		if day_of_week != None:
			self.day_of_week = day_of_week


	def execute(self, command_list: list = []):
		dest_file: str = f"""{RepeatTask.dest_dir}/{self.job_file}"""

		with open(dest_file, "w") as job:
			first: bool = True
			for line in command_list:
				job.write(f"""{line}\n""")

		os.chmod(dest_file, 0o711)
		cmd: str = f"""(/usr/bin/crontab -l 2>/dev/null; echo "{self.minute} {self.hour} {self.day} {self.month} {self.day_of_week} {dest_file}") | /usr/bin/crontab -"""
		# print(cmd)
		result = subprocess.run(cmd, shell = True)
		return result


class OneTimeTask:
	dest_dir: str = f"""/var/pyad/jobs/at"""

	def __init__(self, name: str = None):
		self.time = ""
		
		if not os.path.isdir(OneTimeTask.dest_dir):
			os.makedirs(OneTimeTask.dest_dir, mode=0o700)
		
		if name != None:
			split_tup = os.path.splitext(name)
		
			file_name = split_tup[0]
			file_extension = split_tup[1]

			if len(file_extension) == 0:
				name = name + ".sh"

		self.job_file = name if name != None else f"""{uuid.uuid4()}.sh"""


	def set_absolute_time(self, time: datetime):
		self.time = f"""{time.hour:02d}:{time.minute:02d} {time.strftime("%b").lower()} {time.day:02d}  {time.year}"""

	
	def execute(self, command_list: list = [], keep_job_file: bool = False, print_result: bool = True):
		dest_file: str = f"""{OneTimeTask.dest_dir}/{self.job_file}"""

		with open(dest_file, "w") as job:
			for line in command_list:
				job.write(f"""{line}\n""")

			if not keep_job_file:
				job.write(f"""/usr/bin/rm {dest_file}\n""")

		os.chmod(dest_file, 0o711)
		cmd: str = f"""/usr/bin/at {self.time} -f "{dest_file}" """
		result = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

		if print_result:		
			if result.returncode == 0:
				print(f"""Created task {self.job_file}""")
			else:
				print(f"""Error during creating task {self.job_file}: {result.stdout[0:-1].decode('ascii')}""")

		return result

