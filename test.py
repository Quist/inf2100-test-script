#!/usr/bin/env python3
import sys
import subprocess,threading
import os
import argparse

#Define paths
dirname = os.path.dirname(sys.argv[0])
compiler_path = dirname + '/../Cflat.jar'
testfiles_dir = dirname + '/testfiles/'
output_dir = dirname + '/output/'

compile_timeout = 2

def main():
	args = parse_args()
	compile_files(get_target_files(args.path))
	#init_output_folder()

def parse_args():
	parser = argparse.ArgumentParser(description='automate your compile testing')
	parser.add_argument('path', nargs='?', default=testfiles_dir,help='optionaly specify path to a file or folder to test')
	return parser.parse_args()

def get_target_files(path):
	if path.endswith('/'):
		return get_cflat_files(path)
	else :
		return [args.path]

def compile_files(target_paths):
	compiler = Compiler()
	for filepath in target_paths:
		compiler.compile(filepath,compile_timeout)

def init_output_folder():
	if os.path.exists(output_dir):
		clean(output_dir)
	else:
		os.makedirs(output_dir)

def save_log_files(_dir):
	filelist = [ f for f in os.listdir(_dir) if f.endswith(".log") or f.endswith(".s")]
	for f in filelist:
		os.rename(_dir + f,output_dir+f)

def clean(_dir):
	filelist = [ f for f in os.listdir(_dir) if f.endswith(".log") or f.endswith(".s")  ]
	for f in filelist:
		os.remove(_dir +f)

def get_cflat_files(dir_path):
	filelist = [ dir_path + f  for f in os.listdir(dir_path) if f.endswith(".cflat")]
	return filelist

class Compiler():
	def __init__(self):
		self.cmd = 'java -jar ' + compiler_path + ' -testparser '
		self.process = None
		self.err_out = None

	def compile(self,filepath,timeout):
		def target():
			cmd = self.cmd + filepath
			self.process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			self.err_out = str(self.process.communicate()[1])

		def check_thread():
			print("------------------------------------------")
			if thread.is_alive():
				self.process.terminate()
				thread.join()
				self.on_timeout()
			elif self.process.returncode != 0:
				print(self.on_compile_error())
			else:
				print(self.print_success())

		self.filename = os.path.split(filepath)[1]
		thread = threading.Thread(target=target)
		thread.start()
		thread.join(timeout)
		check_thread()


	def on_compile_error(self):
		print_error(self.err_out)

	def on_timeout(self):
		self.print_error("Timeout after %d seconds" %compile_timeout)
	
	def print_error(self,msg):
		print("%s: ERROR" %(self.filename))
		print("Output:")
		print("\t%s" %msg)

	def print_success(self):
		print("%s: OK" %(self.filename))
main()

