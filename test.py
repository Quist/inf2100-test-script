#!/usr/bin/env python3
import sys
import subprocess,threading
import os
import argparse

#Define paths
testfiles_dir = os.path.dirname(sys.argv[0]) + '/testfiles/'
#output_dir = dirname + '/output/'


class CompileTester:
	def __init__(self):
		self.args = parse_args()
		self.path = os.path.dirname(sys.argv[0])
		project_root_path = self.path + '/../'
		self.compiler = Compiler(project_root_path)

		#Do the testing
		print("\n\nstarting testing..\n")
		self.compile_files()

	def compile_files(self):
		target_paths = get_target_files(self.args.path)
		successfull_compilations = 0
		for filepath in target_paths:
			basename = os.path.basename(filepath)
			try:
				self.compiler.compile(filepath)
				successfull_compilations+= 1
				self.print_success(basename)
			except CompileException as e:
				self.print_error(str(e),basename)
			except TimeoutException as e:
				self.print_error(str(e),basename)

		print("\n%d/%d successfull tests\n" %(successfull_compilations,len(target_paths)))
	
	def print_error(self,msg,basename):
		print("%s: ERROR" %(basename))
		print("Output:")
		print("\t%s" %msg)
		print("------------------------------------------")

	def print_success(self,basename):
		print("%s: OK" %(basename))
		print("------------------------------------------")
	
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

class Compiler():
	compile_timeout = 2
	def __init__(self,root_path):
		self.compile_cmd = 'java -jar ' + root_path + 'Cflat.jar -testparser '
		self.root_path = root_path
		self.build_compiler()

	def build_compiler(self):
		cur_dir = os.getcwd()
		os.chdir(self.root_path)
		process = subprocess.Popen("ant")
		process.communicate()
		os.chdir(cur_dir)

		
	def compile(self,filepath):
		def target():
			cmd = self.compile_cmd + filepath
			self.process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
			self.err_out = str(self.process.communicate()[1])

		def check_thread():
			if thread.is_alive():
				self.process.terminate()
				thread.join()
				raise TimeoutException()
			elif self.process.returncode != 0:
				raise CompileException(self.err_out)

		self.filename = os.path.split(filepath)[1]
		thread = threading.Thread(target=target)
		thread.start()
		thread.join(self.compile_timeout)
		check_thread()

class TimeoutException(Exception):
	def __init__(self):
		Exception.__init__(self,"Timeout after %d seconds" %Compiler.compile_timeout)

class CompileException(Exception):
	def __init__(self, message):
		Exception.__init__(self,message)


def parse_args():
	parser = argparse.ArgumentParser(description='automate your compile testing')
	parser.add_argument('path', nargs='?', default=testfiles_dir,help='optionaly specify path to a file or folder to test')
	return parser.parse_args()

def get_target_files(path):
	if path.endswith('/'):
		return get_cflat_files(path)
	else :
		return [path]	

def get_cflat_files(dir_path):
	filelist = [ dir_path + f  for f in os.listdir(dir_path) if f.endswith(".cflat")]
	return filelist

test = CompileTester()