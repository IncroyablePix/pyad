import os
import sys
import subprocess
import _io
from subprocess import PIPE
from pyad.utils.colors import TColor
from pyad.net.utils import bits_to_mask
from abc import ABC, abstractmethod

		
def tabs(depth: int = 0):
	if depth > 0:
		return "".join(["\t"] * depth)
		
	return ""


class DHCPGroup(ABC):
	def __init__(self):
		self.domain_name_servers = []
		self.ntp_servers = []
		
		
	def set_domain_name(self, domain_name: str = ""):
		self.domain_name = domain_name

		
	def add_dns(self, dns = None):
		if type(dns) is list:
			for srv in dns:
				self.add_dns(srv)
		elif type(dns) is str:
			if dns not in self.domain_name_servers:
				self.domain_name_servers.append(dns)
		
		
	def add_ntp(self, ntp = None):
		if type(ntp) is list:
			for srv in ntp:
				self.add_ntp(srv)
		elif type(ntp) is str:
			if dns not in self.ntp_servers:
				self.ntp_servers.append(ntp)
				
	
	def set_default_lease_time(self, default_lease_time: int = 0):
		self.default_lease_time = default_lease_time
		
	
	def set_max_lease_time(self, max_lease_time: int = 0):
		self.max_lease_time = max_lease_time if max_lease_time > self.default_lease_time else self.default_lease_time
		
		
	def set_ddns_update_style(self, ddns_update_style: bool = True):
		self.ddns_update_style = ddns_update_style
		
		
	def set_authoritative(self, authoritative: bool = True):
		self.authoritative = authoritative
		
		
	def set_log_facility(self, log_facility: str = ""):
		self.log_facility = log_facility
		
		
	@abstractmethod
	def write(self, path: str = "", conf_file: _io.TextIOWrapper = None, depth: int = 0):
		pass
		
		
class DHCPSubnet(DHCPGroup):
	def __init__(self, network: str = "", mask: int = "24"):
		super(DHCPSubnet, self).__init__()
		self.network = network
		self.mask = bits_to_mask(mask)
		self.subnets = []
		self.range_min = None
		self.range_max = None
		self.routers = []
		self.deny_unknown = False
		self.broadcast_address = None
		self.hosts = []
	
	
	def set_range(self, range_min: str = None, range_max: str = None):
		self.range_min = range_min
		self.range_max = range_max
		
		
	def set_broadcast_address(self, broadcast_address: str = None):
		self.broadcast_address = broadcast_address
		
		
	def add_router(self, router = None):
		if type(router) is list:
			for r in router:
				self.add_router(r)
		elif type(router) is str:
			if router not in self.routers:
				self.routers.append(router)
		
	
	def set_deny_unknown(self, deny_unknown: bool = True):
		self.deny_unknown = deny_unknown
		
	
	def add_host(self, host = None):
		if type(host) is list:
			for h in host:
				self.add_host(h)
		elif type(host) is DHCPReservation:
			if host not in self.hosts:
				self.hosts.append(host)
				
				
	def write(self, path: str = "", conf_file: _io.TextIOWrapper = None, depth: int = 0):
		if conf_file != None:
			if self.range_min == None or self.range_max == None:
				raise Exception(message = f"""No range specified for subnet {self.network}""")
			
			conf_file.write(f"""{tabs(depth)}subnet {self.network} netmask {self.mask} {"{"}\n""")
			conf_file.write(f"""{tabs(depth + 1)}range {self.range_min} {self.range_max};\n""")

			if self.broadcast_address != None:
				conf_file.write(f"""{tabs(depth + 1)}option broadcast-address {self.broadcast_address};\n""")
				
			if len(self.routers) > 0:
				conf_file.write(f"""{tabs(depth + 1)}option routers {", ".join(self.routers)};""")
				
			if getattr(self, "domain_name", None) and self.domain_name != None:
				conf_file.write(f"""{tabs(depth + 1)}option domain-name "{self.domain_name};"\n""")
					
			if len(self.domain_name_servers) > 0:
				conf_file.write(f"""{tabs(depth + 1)}option domain-name-servers {", ".join(self.domain_name_servers)};\n""")
				
			if getattr(self, "default_lease_time", None) and self.default_lease_time != None:
				conf_file.write(f"""{tabs(depth + 1)}default-lease-time {self.default_lease_time};\n""")
				
			if getattr(self, "max_lease_time", None) and self.max_lease_time != None:
				conf_file.write(f"""{tabs(depth + 1)}max-lease-time {self.max_lease_time};\n""")
				
			if len(self.hosts) > 0:
				for host in self.hosts:
					conf_file.write("\n")
					host.write(conf_file = conf_file, depth = depth)
					conf_file.write("\n")
					
			conf_file.write(f"""{tabs(depth)}{"}"}\n""")
		
		
class DHCPReservation:
	def __init__(self, reservation_name: str = "", hardware_type: str = "ethernet", ip: str = None, mac_address: str = None):
		super(DHCPReservation, self).__init__()
		self.reservation_name = reservation_name
		self.mac_address = mac_address
		self.hardware_type = hardware_type
		self.ip = ip
		
		
	def set_ip(self, ip: str = None):
		self.ip = ip
		
		
	def set_mac_address(self, mac_address: str = None):
		self.mac_address = mac_address
		
		
	def write(self, path: str = "", conf_file: _io.TextIOWrapper = None, depth: int = 0):
		if conf_file != None:
			if len(self.reservation_name) == 0:
				raise Exception(message = f"""A reservation cannot be nameless""")
			if self.mac_address == None or self.ip == None:
				raise Exception(message = f"""No MAC address or IP specified for host {self.reservation_name}""")
			
			conf_file.write(f"""{tabs(depth)}host {self.reservation_name} {"{"}\n""")
			conf_file.write(f"""{tabs(depth + 1)}hardware {self.hardware_type} {self.mac_address};\n""")
			conf_file.write(f"""{tabs(depth + 1)}fixed-address {self.ip};\n""")
					
			conf_file.write(f"""{tabs(depth)}{"}"}\n""")
			
			
class DHCPSharedNetwork(DHCPGroup):
	def __init__(self, network_name: str = ""):
		super(DHCPSharedNetwork, self).__init__()
		self.network_name = network_name
		self.subnets = []
				
				
	def add_subnet(self, subnet = None):
		if type(subnet) is list:
			for sub in subnet:
				self.add_subnet(sub)
		elif type(subnet) is DHCPSubnet:
			if subnet not in self.subnets:
				self.subnets.append(subnet)
				
				
	def write(self, path: str = "", conf_file: _io.TextIOWrapper = None, depth: int = 0):
		if conf_file != None:
			if self.range_min == None or self.range_max == None:
				raise Exception(message = f"""No range specified for subnet {self.network}""")
			
			conf_file.write(f"""{tabs(depth)}shared-network {self.network_name} {"{"}\n""")
			conf_file.write(f"""{tabs(depth + 1)}range {self.range_min} {self.range_max};\n""")

			if self.broadcast_address != None:
				conf_file.write(f"""{tabs(depth + 1)}option broadcast-address {self.broadcast_address};\n""")
				
			if len(self.routers) > 0:
				conf_file.write(f"""{tabs(depth + 1)}option routers {", ".join(self.routers)};""")
				
			if self.domain_name != None:
				conf_file.write(f"""{tabs(depth + 1)}option domain-name "{self.domain_name};"\n""")
					
			if len(self.dns) > 0:
				conf_file.write(f"""{tabs(depth + 1)}option domain-name-servers {", ".join(self.domain_name_servers)};\n""")
				
			if self.default_lease_time != None:
				conf_file.write(f"""{tabs(depth + 1)}default-lease-time {self.default_lease_time};\n""")
				
			if self.max_lease_time != None:
				conf_file.write(f"""{tabs(depth + 1)}max-lease-time {self.max_lease_time};\n""")
				
			if len(self.subnets) > 0:
				for sub in self.subnets:
					conf_file.write("\n")
					sub.write(conf_file = conf_file, depth = depth + 1)
					conf_file.write("\n")
					
			conf_file.write(f"""{tabs(depth)}{"}"}\n""")


class DHCPGlobal(DHCPGroup):	

	__DHCPD_CONF_FILE = """/etc/dhcp/dhcpd.conf"""
	
	def __init__(self, domain_name: str = "", dns: list = [], default_lease_time: int = 14400, max_lease_time: int = 14400, ntp_servers: list = [], ddns_update_style: bool = True, authoritative: bool = True, log_facility: str = "local7"):
		super(DHCPGlobal, self).__init__()
		self.set_domain_name(domain_name = domain_name)
		self.add_dns(dns = dns)
		self.set_default_lease_time(default_lease_time = default_lease_time)
		self.set_max_lease_time(max_lease_time = max_lease_time)
		self.add_ntp(ntp = ntp_servers)
		self.set_ddns_update_style(ddns_update_style = ddns_update_style)
		self.set_authoritative(authoritative = authoritative)
		self.set_log_facility(log_facility = log_facility)
		self.subnets = []
		self.shared_networks = []
		self.hosts = []
		
	
	def add_host(self, host = None):
		if type(host) is list:
			for h in host:
				self.add_host(h)
		elif type(host) is DHCPReservation:
			if host not in self.hosts:
				self.hosts.append(host)
		
	
	def add_subnet(self, subnet = None):
		if type(subnet) is list:
			for sub in subnet:
				self.add_subnet(sub)
		elif type(subnet) is DHCPSubnet:
			if subnet not in self.subnets:
				self.subnets.append(subnet)
				

	def add_shared_network(self, sn = None):
		if type(sn) is list:
			for net in sn:
				self.add_shared_network(net)
		elif type(sn) is DHCPSubnet:
			if sn not in self.shared_networks:
				self.shared_networks.append(sn)
			
	
	def write(self, path: str = """/etc/dhcp/dhcpd.conf""", conf_file: _io.TextIOWrapper = None, depth: int = 0) -> bool:
		no_error = True
		if conf_file == None:
			print(f"""{TColor.OKGREEN}Writing DHCP config file...{TColor.ENDC}""")
			with open(path, "w+") as f:
				no_error = self.write(conf_file = f)
			
			if no_error:
				print(f"""{TColor.OKGREEN}Done without error!{TColor.ENDC}""")
			else:
				print(f"""{TColor.FAIL}Done with errors...{TColor.ENDC}""")
			
		else:
			
			if self.domain_name != None:
				conf_file.write(f"""{tabs(depth)}option domain-name "{self.domain_name}";\n""")
					
			if len(self.domain_name_servers) > 0:
				conf_file.write(f"""{tabs(depth)}option domain-name-servers {", ".join(self.domain_name_servers)};\n""")
				
			if self.default_lease_time != None:
				conf_file.write(f"""{tabs(depth)}default-lease-time {self.default_lease_time};\n""")
				
			if self.max_lease_time != None:
				conf_file.write(f"""{tabs(depth)}max-lease-time {self.max_lease_time};\n""")
				
			if self.authoritative == True:
				conf_file.write(f"""{tabs(depth)}authoritative;\n""")

			if self.log_facility != None and len(self.log_facility) > 0:
				conf_file.write(f"""{tabs(depth)}log-facility {self.log_facility};\n""")
				
			if len(self.subnets) > 0:
				print(f"""{TColor.OKGREEN}=> writing DHCP subnets...{TColor.ENDC}""")
				for sub in self.subnets:
					conf_file.write("\n")
					try:
						sub.write(conf_file = conf_file, depth = depth)
					except Exception as e:
						print(f"""{TColor.FAIL}Warning: {TColor.WARNING}{e.message}{TColor.ENDC}""")
						
					conf_file.write("\n")
				
			if len(self.shared_networks) > 0:
				print(f"""{TColor.OKGREEN}=> writing DHCP shared networks...{TColor.ENDC}""")
				for net in self.shared_networks:
					conf_file.write("\n")
					try:
						net.write(conf_file = conf_file, depth = depth)
					except Exception as e:
						print(f"""{TColor.FAIL}Warning: {TColor.WARNING}{e.message}{TColor.ENDC}""")
					conf_file.write("\n")
				
			if len(self.hosts) > 0:
				print(f"""{TColor.OKGREEN}=> writing DHCP hosts...{TColor.ENDC}""")
				for host in self.hosts:
					conf_file.write("\n")
					try:
						host.write(conf_file = conf_file, depth = depth)
					except Exception as e:
						print(f"""{TColor.FAIL}Warning: {TColor.WARNING}{e.message}{TColor.ENDC}""")
					conf_file.write("\n")
				
			'''if self.ddns_update_style != None:
				conf_file.write(f"""option {self.domain_name}\n""")
			if self.domain_name != None:
				conf_file.write(f"""option {self.domain_name}\n""")'''
				
		return no_error
		
		
'''
	Lease time:
	- 14400 (4h) -> A lot of mobile devices
	- 28800 (8h) -> Mobile devices
	- 86400 (1d)
	- 691200 (8d) -> Desktop PC
'''
