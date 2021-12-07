import os
import sys
import subprocess
import datetime
import uuid

'''TODO: Pour  des  raisons  de  sécurité,  il  est  possible  de  limiter  les  utilisateurs  autorisés  à  exécuter  ces 
commandes. Par défaut, tous les utilisateurs peuvent programmer des tâches ponctuelles ou 
répétitives sur les systèmes RHEL 8. Il est possible de limiter les utilisateurs en ajoutant des éléments 
dans /etc/cron.allow, /etc/cron.deny, /etc/at.allow ou /etc/at.deny. Pour plus 
d’information, référez-vous aux pages de manuel de ces commandes.'''

class RepeatTask:
	def __init__(self):
		pass


	def set_time(self):
		pass


	def execute(self):
		pass


class OneTimeTask:
	dest_dir: str = f"""/var/pyad/jobs"""

	def __init__(self):
		self.time = ""
		
		if not os.path.isdir(OneTimeTask.dest_dir):
			os.makedirs(OneTimeTask.dest_dir, mode=0o700)

		self.job_file = f"""{uuid.uuid4()}.sh"""


	def set_absolute_time(self, time: datetime):
		self.time = f"""{time.hour:02d}:{time.minute:02d} {time.strftime("%b").lower()} {time.day:02d}  {time.year}"""

	
	def execute(self, command_list: list = [], keep_job_file: bool = False):
		dest_file: str = f"""{OneTimeTask.dest_dir}/{self.job_file}"""

		with open(dest_file, "w") as job:
			for line in command_list:
				job.write(f"""{line}\n""")

			if not keep_job_file:
				job.write(f"""/usr/bin/rm {dest_file}\n""")

		cmd: str = f"""/usr/bin/at {self.time} -f "{dest_file}" """
		result = subprocess.run(cmd, shell = True)
		return result
