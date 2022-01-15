import os
import subprocess

__SYSTEM_DAEMON_LOCAL = "/etc/rc.d/rc.local"

def add_boot_cmds(cmd_list: list = []):
	with open(__SYSTEM_DAEMON_LOCAL, """a""") as temp_file:
		for cmd in cmd_list:
			temp_file.write(f"{cmd}\n")

	os.chmod(__SYSTEM_DAEMON_LOCAL, 0o744)

