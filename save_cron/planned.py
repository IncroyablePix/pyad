import os
import sys
import subprocess
import datetime

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


class OntTimeTask:
	def __init(self):
		self.time = ""


	def set_absolute_time(self, time: datetime):
		self.time = f"""{time.strftime("%a")} {time.strftime("%b")} {time.day:02d} {time.hour:02d}:{time.minute:02d}:{time.second:02d} {time.year}"""

	
	def execute(self, command: str = ""):
		result = subprocess.run(f"""at {self.time} -f "{command}" """, shell = True)
		return result
