import os
import sys
import subprocess
import re
from pyad.utils.colors import TColor

def add_authentication(path: str = None, pass_path: str = "/etc/httpd/apache-users.pass", message: str = "Please log in to continue"):
	if path != None:
		htaccess_file = f"""{path}/.htaccess"""
		dir_name = os.path.dirname(htaccess_file)
		
		if not os.path.exists(dir_name):
			os.makedirs(dir_name)
			result = subprocess.run(f"""/usr/bin/chown apache:apache {dir_name}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			if result.returncode != 0:
				print(f"""{TColor.FAIL}Error in apache passwd creation: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
				return
				
			result = subprocess.run(f"""/usr/bin/chown apache:apache {pass_path}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
			if result.returncode != 0:
				print(f"""{TColor.FAIL}Error in apache passwd creation: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
				return
				
		with open(htaccess_file, "a") as f:
			f.write(f"""AuthType Basic\n""")
			f.write(f"""AuthName "{message}"\n""")
			f.write(f"""AuthBasicProvider file\n""")
			f.write(f"""AuthUserFile "{pass_path}"\n""")
			f.write(f"""Require valid-user\n""")

		result = subprocess.run(f"""/usr/bin/chown apache:apache {htaccess_file}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
		if result.returncode != 0:
			print(f"""{TColor.FAIL}Error in .htaccess creation: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
		else:
			print(f"""{TColor.OKGREEN}Added authentication for '{path}'.{TColor.ENDC}""")
			
			

def add_tls_private_key(path: str = "", password: str = "", print_result: bool = True):
	file_name = path.split("/")[-1]
	new_path = f"""/etc/pki/tls/private"""
	print(path, new_path)
	result = subprocess.run(f"""/usr/bin/cp {path} {new_path}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
	os.chown(new_path, 0, 0) # uid 0 = root / gid 0 = root
	os.chmod(new_path, 0o600)
	
	if print_result:
		if result.returncode == 0:
			print(f"""{TColor.OKGREEN}Added private key '{path}'.{TColor.ENDC}""")
		else:
			print(f"""{TColor.FAIL}Error adding private key: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")
			
	
	
def toggle_users_websites(toggle: bool = True, home_base: str = "/home", directory: str = "public_html", path: str = "/etc/httpd/conf.d/userdir.conf", print_result: bool = True):
	lines = []
	
	with open(path, """r""") as temp_file:
		for line in temp_file:
			userdir_pattern = re.compile(r"""[ |\t]+UserDir[\s]*([\/\w\d_\-\.]+)""")
			directory_pattern = re.compile(r"""<Directory\s+"(.+)">""")
			match_userdir = userdir_pattern.match(line.rstrip())
			match_directory = directory_pattern.match(line.rstrip())
			
			if match_userdir:
				lines.append(line.replace(match_userdir.group(1), directory))
			elif match_directory:
				lines.append(line.replace(match_directory.group(1), f"""{home_base}/*/{directory}"""))
			else:
				lines.append(line)
	            
	with open(path, """w""") as temp_file:
		for line in lines:
			temp_file.write(line)


	print(f"""{TColor.OKGREEN}UserDir set to {directory}.{TColor.ENDC}""")
