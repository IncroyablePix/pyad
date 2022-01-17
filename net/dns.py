import datetime
from subprocess import PIPE
from pyad.utils.colors import TColor
from abc import ABC, abstractmethod

class DNSEntry:
	def __init__(self, location: str = None, priority: int = None):
		self.location = location
		self.priority = priority
		
	
	def get_line(self, domain_name: str = "") -> str:
		entry = """\t\t\tIN\tNS\t"""
		
		if self.priority != None:
			entry = entry + f"""{self.priority}\t"""
			
		entry = entry + f"""{self.location}.{domain_name}."""
		return entry
		

class MXEntry:
	def __init__(self, location: str = None, priority: int = None):
		self.location = location
		self.priority = priority
		
	
	def get_line(self, domain_name: str = "") -> str:
		entry = """\t\t\tIN\tMX\t"""
	
		if priority != None:
			entry = entry + f"""{self.priority}\t"""
			
		entry = entry + f"""{self.location}.{domain_name}"""
		return entry
		
	
class DNSRecord:
	def __init__(self, location: str = "", entry_type: str = "CNAME", priority: int = None, pointer: str = ""):
		self.entry_type = entry_type
		self.priority = priority
		self.location = location
		self.pointer = pointer
		
		
	def get_line(self) -> str:
		return f"""{self.location}\t\tIN\t{self.entry_type}\t{self.pointer}"""
		
		
class DNSFile(ABC):
	def __init__(self, domain_name: str = "", ttl: int = 86400, serial: int = None, refresh: int = 28800, retry: int = 14400, expire: int = 3600000, name_error: int = 3600, soa: bool = True):
		if serial == None:
			today = datetime.datetime.now() 
			self.serial = f"""{today.year}{today.month}{today.day}01"""
		else:
			self.serial = serial
			
		self.domain_name = domain_name
		self.ttl = ttl
		self.refresh = refresh
		self.retry = retry
		self.expire = expire
		self.name_error = name_error
		self.soa = soa
		self.mxs = []
		self.dns = []
		self.records = []
		self.ptrs = []
	
		
	def set_domain_name(self, domain_name: str = None):
		self.domain_name = domain_name
		
		
	def add_dns(self, dns = None):
		if type(dns) is list:
			for srv in dns:
				self.add_dns(srv)
		elif type(dns) is DNSEntry:
			if dns not in self.dns:
				self.dns.append(dns)
	
		
	def add_mx(self, mx = None):
		if type(mx) is list:
			for record in mx:
				self.add_mx(record)
		elif type(mx) is MXEntry:
			if mx not in self.mxs:
				self.mxs.append(mx)
	
		
	def add_record(self, record = None):
		if type(record) is list:
			for r in record:
				self.add_record(r)
		elif type(record) is DNSRecord:
			if record not in self.records:
				self.records.append(record)
	
		
	def add_ptr(self, ptr = None):
		if type(ptr) is list:
			for p in ptr:
				self.add_ptr(p)
		elif type(ptr) is DNSPointer:
			if ptr not in self.ptrs:
				self.ptrs.append(ptr)
		
		

class DNSZone(DNSFile):
	def __init__(self, domain_name: str = None, ttl: int = 86400, serial: int = None, refresh: int = 28800, retry: int = 14400, expire: int = 3600000, name_error: int = 3600, soa: bool = True):
		super(DNSZone, self).__init__(domain_name = domain_name, ttl = ttl, serial = serial, refresh = refresh, retry = retry, expire = expire, name_error = name_error, soa = soa)
		
		
	def write(self, scope: str = "internal", path: str = """/var/named/chroot/var/named""", print_result: bool = True):
		if print_result: 
			print(f"""{TColor.OKGREEN}Writing {scope} DNS Zone ({self.domain_name})...{TColor.ENDC}""")
			
			
		with open(f"""{path}/db.{self.domain_name}.{scope}""", "w+") as f:
			f.write(f"""$TTL\t{self.ttl}\n""")
			f.write(f"""@\tIN\t""")
			if self.soa:
				f.write("SOA\t")
			f.write(f"""{self.domain_name}.\t\troot.{self.domain_name}. (\n""")
			
			f.write(f"""\t\t\t\t{self.serial}\t; Serial (increment by one when modified)\n""")
			f.write(f"""\t\t\t\t{self.refresh}\t; Refresh\n""")
			f.write(f"""\t\t\t\t{self.retry}\t; Retry\n""")
			f.write(f"""\t\t\t\t{self.expire}\t; Expire\n""")
			f.write(f"""\t\t\t\t{self.name_error}\t; Name error\n)\n\n""")
			
			
			if print_result: 
				print(f"""{TColor.OKGREEN}Writing DNS Servers...{TColor.ENDC}""")
				
			# DNS Servers
			f.write(f"""; ### DNS Servers ###\n""")
			f.write("\n".join(map(lambda d: d.get_line(domain_name = self.domain_name), self.dns)) + "\n\n")
			
			if print_result: 
				print(f"""{TColor.OKGREEN}Writing Mail Servers...{TColor.ENDC}""")
							
			# Mail Servers
			f.write(f"""; ### Mail Servers ###\n""")
			f.write("\n".join(map(lambda mx: mx.get_line(domain_name = self.domain_name), self.mxs)) + "\n\n")
			
			
			# Records
			f.write(f"""; ### DNS Records ###\n""")
			f.write("\n".join(map(lambda r: r.get_line(), self.records)) + "\n\n")
			
			if print_result: 
				print(f"""{TColor.OKGREEN}Done.{TColor.ENDC}""")
		

class DNSPointer:
	def __init__(self, endpoint: int = 0, full_name: str = None):
		self.endpoint = endpoint
		self.full_name = full_name
		
	
	def get_line(self) -> str:
		return f"""{self.endpoint}\t\tIN\tPTR\t{self.full_name}"""
		
		
		
class DNSReverse(DNSFile):
	def __init__(self, domain_name: str = "", ip: str = None, ttl: int = 86400, serial: int = None, refresh: int = 28800, retry: int = 14400, expire: int = 3600000, name_error: int = 3600, soa: bool = True):
		super(DNSReverse, self).__init__(domain_name = domain_name, ttl = ttl, serial = serial, refresh = refresh, retry = retry, expire = expire, name_error = name_error, soa = soa)
		self.ip = ".".join(ip.split(".")[0:3])
	
		
	def write(self, path: str = """/var/named/chroot/var/named""", print_result: bool = True):
		if print_result: 
			print(f"""{TColor.OKGREEN}Writing DNS Reverse Lookup Zone ({self.ip}.x)...{TColor.ENDC}""")
			
		with open(f"""{path}/db.{self.ip}""", "w+") as f:
			f.write(f"""$TTL\t{self.ttl}\n""")
			f.write(f"""@\tIN\t""")
			if self.soa:
				f.write("SOA\t")
			f.write(f"""{self.domain_name}.\t\troot.{self.domain_name}. (\n""")
			
			f.write(f"""\t\t\t\t{self.serial}\t; Serial (increment by one when modified)\n""")
			f.write(f"""\t\t\t\t{self.refresh}\t; Refresh\n""")
			f.write(f"""\t\t\t\t{self.retry}\t; Retry\n""")
			f.write(f"""\t\t\t\t{self.expire}\t; Expire\n""")
			f.write(f"""\t\t\t\t{self.name_error}\t; Name error\n)\n\n""")
			
			
			if print_result: 
				print(f"""{TColor.OKGREEN}Writing DNS Servers...{TColor.ENDC}""")
				
			# DNS Servers
			f.write(f"""; ### DNS Servers ###\n""")
			f.write("\n".join(map(lambda d: d.get_line(domain_name = self.domain_name), self.dns)) + "\n\n")
			
			if print_result: 
				print(f"""{TColor.OKGREEN}Writing Mail Servers...{TColor.ENDC}""")
							
			# Mail Servers
			f.write(f"""; ### Mail Servers ###\n""")
			f.write("\n".join(map(lambda mx: mx.get_line(domain_name = self.domain_name), self.mxs)) + "\n\n")
			
			
			# Records
			f.write(f"""; ### DNS Records ###\n""")
			f.write("\n".join(map(lambda ptr: ptr.get_line(), self.ptrs)) + "\n\n")
			
			if print_result: 
				print(f"""{TColor.OKGREEN}Done.{TColor.ENDC}""")
		
	
