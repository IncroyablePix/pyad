import os
import sys
import subprocess
import re
from abc import ABC, abstractmethod


class Archive(ABC):
	@abstractmethod
	def archive_dir(self, archive_path: str = None, files: str = None, recursive: bool = True):
		pass

	@abstractmethod
	def extract_archive(self, archive_path: str = None, extract_path: str = None):
		pass

	@abstractmethod
	def list(self, archive_path: str = None):
		pass


class ZipArchive(Archive):
	def archive_dir(self, archive_path: str = None, files: str = None, recursive: bool = True):
		if not (archive_path == None or files == None):
			options: str = ""

			if recursive:
				options += " -r "

			result = subprocess.run(f"""/usr/bin/zip {options} {archive_path} {files}""", shell = True)
			return result

		return ""


	def extract_archive(self, archive_path: str = None, extract_path: str = None):
		if not (archive_path == None or extract_path == None):
			options: str = ""
			if extract_path == None:
				options += f""" -d {extract_path} """

			result = subprocess.run(f"""/usr/bin/unzip {archive_path}""", shell = True)
			return result

		return ""


	def list(self, archive_path: str = None):
		if not (archive_path == None):
			result = subprocess.run(f"""/usr/bin/unzip -l {archive_path}""", shell = True)
			return result

		return ""



class TarArchive(Archive):
	compression_args = {
		"gz": "z",
		"bz2": "j",
		"xz": "J"
	}

	def __init__(self, compression: str = None):
		self.compression = TarArchive.compression_args.get(compression, "z") # default is gz


	def archive_dir(self, archive_path: str = None, files: str = None, recursive: bool = True):
		if not (archive_path == None or files == None):
			options: str = f"""-cv{self.compression}f"""

			result = subprocess.run(f"""/usr/bin/tar {options} {archive_path} {files}""", shell = True)
			return result

		return ""


	def extract_archive(self, archive_path: str = None, extract_path: str = None):
		if not (archive_path == None or extract_path == None):
			options: str = f"""-xv{self.compression}f"""

			extract: str = "" if extract_path == None else f""" -C {extract_path} """

			result = subprocess.run(f"""/usr/bin/tar {options} {archive_path} {extract}""", shell = True)
			return result

		return ""


	def list(self, archive_path: str = None):
		if not (directory == None or files == None):
			options: str = f"""-tv{self.compression}f"""

			result = subprocess.run(f"""/usr/bin/tar {options} {archive_path}""", shell = True)
			return result

		return ""



