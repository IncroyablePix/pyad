import os
import sys
import subprocess
from pyad.utils.colors import TColor

class DockerImage:
	def __init__(self, image_name: str = None, version: str = None):
		self.image_name = image_name
		self.version = version
		
	
	def pull(self, print_result: bool = True):
		if self.image_name == None:
			if print_result:
				print(f"""{TColor.FAIL}Error in local user creation: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
				return
				
		v = ""
		
		if self.version != None:
			v = f""":{self.version}"""
		
		result = subprocess.run(f"""/usr/bin/docker pull {self.image_name}{v}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Docker image '{self.image_name}' pulled.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Failed to pull docker image '{self.image_name}': {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
				
				
	def run(self, name: str = None, host_port: int = None, container_port: int = None, host_dir: str = None, container_dir: str = None, maintain: bool = False, print_result: bool = True):
	
		cmd = f"""/usr/bin/docker run -d"""
		
		if name != None:
			cmd += f""" --name {name}"""
			
		if container_port != None and host_port != None:
			cmd += f""" -p {host_port}:{container_port}""" 
			
			
		if host_dir != None and container_dir != None:
			cmd += f""" -v {host_dir}:{container_dir}"""
			
		
		### 
		
		cmd += f""" {self.image_name}"""		
		
		if self.version != None:
			cmd += f""":{self.version}"""
		
		
		if maintain:
			cmd += " tail -f /dev/null"
		
		print(cmd)
		result = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Docker image '{self.image_name}' started as '{name}'.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Failed to run docker image '{self.image_name}': {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
		
		return DockerContainer(name = name)
		
		

class DockerContainer:
	def __init__(self, name: str = None):
		self.name = name
		
		
	def cmd(self, cmd: str = ""):
		result = subprocess.run(f"""/usr/bin/docker exec {self.name} /bin/bash -c '{cmd}'""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Executing command '{cmd}' on '{self.name}':{TColor.ENDC}\n{result.stdout[0:-1].decode('ascii')}""")
			else:
				print(f"""{TColor.FAIL}Failed to execute command '{cmd}' on docker image '{self.name}': {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
		
		
	def stop(self, print_result: bool = True):
		result = subprocess.run(f"""/usr/bin/docker stop {self.name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Docker container '{self.name}' stopped.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Failed to stop docker container '{self.name}': {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
	
	
	def remove(self, print_result: bool = True):
		result = subprocess.run(f"""/usr/bin/docker rm {self.name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if print_result:
			if result.returncode == 0:
				print(f"""{TColor.OKGREEN}Docker image '{self.name}' removed.{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Failed to remove docker image '{self.name}': {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
