import os
import sys
import subprocess
import re
from pyad.utils.colors import TColor

def mount_net_disk(net_path: str = "", path: str = "", user_name: str = "", domain: str = None, password: str = ""):
	dom = ""
	if domain != None:
		dom += f""",domain={domain}"""
		
	result = subprocess.run(f"""/usr/bin/mount -t cifs {net_path} {path} -o username={user_name}{dom},password={password}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

	if result.returncode == 0:
		print(f"""{TColor.OKGREEN}Mounted Network path '{net_path}' to '{path}'{TColor.ENDC}""")
	else:
		print(f"""{TColor.FAIL}Failed to mount network path: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")

def unmount_net_disk(path: str = ""):
	result = subprocess.run(f"""/usr/bin/umount {path}""", shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)

	if result.returncode == 0:
		print(f"""{TColor.OKGREEN}Unmounted Network path '{path}'{TColor.ENDC}""")
	else:
		print(f"""{TColor.FAIL}Failed to unmount network path: {TColor.WARNING}{result.stdout[0:-1].decode('ascii')}{TColor.ENDC}""")

