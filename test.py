#!/usr/bin/env python3
import sys
import subprocess,threading
import os
import argparse

#Define paths
testfile_dirname = os.path.dirname(sys.argv[0]) + '/testfiles/'

class CompileTester:
	def __init__(self):
		self.args = CompileTester.parse_args()
		self.path = os.path.dirname(sys.argv[0])
		self.project_root_path = self.path + '/../'

		if self.build() != 0:
			print("\nbuild failed, exiting..")
			exit()
		print("\nant build successfull")

		CompileTester.clean(testfile_dirname)
		#Do the testing
		print("starting testing..")
		print("compilation timeout: %d seconds\n" %Compiler.compile_timeout)
		self.test()

	def parse_args():
		parser = argparse.ArgumentParser(description='automate your compile testing')
		parser.add_argument('path', nargs='?', default=testfile_dirname,\
			help='specify path/file to test')
		return parser.parse_args()

	def build(self):
		cur_dir = os.getcwd()
		os.chdir(self.project_root_path)
		process = subprocess.Popen("ant",stdout=subprocess.PIPE)
		output = process.communicate()[0]
		os.chdir(cur_dir)
		return process.returncode

	def test(self):
		testcases = self.get_testcases(self.args.path)
		successfull_compilations =0
		for test in testcases:
			test.test()
			print(test)
			successfull_compilations += test.result
			print("--------------------------------------------------")

		print("\n%d/%d successfull tests\n" %(successfull_compilations,len(testcases)))

	def get_testcases(self,path):
		compiler = Compiler(self.project_root_path+'Cflat.jar')
		ref_compiler = Compiler(self.path + '/ref-cflat.jar')
		
		if path.endswith('/'):
			testcases = []
			filelist = [ path + f  for f in os.listdir(path) if f.endswith(".cflat")]
			for f in filelist:
				testcases.append(Testcase(f,compiler,ref_compiler))
			return testcases
		else :
			return [Testcase(path,compiler,ref_compiler)]

	def clean(_dir):
		filelist = [ f for f in os.listdir(_dir) if f.endswith(".log") or \
			f.endswith(".s") or f.endswith(".ref.log")  ]
		for f in filelist:
			os.remove(_dir +f)

class TimeoutException(Exception):
	def __init__(self):
		Exception.__init__(self,"Timeout after %d seconds" %Compiler.compile_timeout)

class CompileException(Exception):
	def __init__(self, message):
		Exception.__init__(self,"\"%s\"" % message.strip('\n'))

class CompareException(Exception):
	def __init__(self, message):
		Exception.__init__(self,"\"%s\"" % message)	

class Testcase():
	def __init__(self,filepath,compiler,ref_compiler):
		self.result = 0
		self.ref_compilator_output = ""
		self.compilator_output =""
		self.differ_output = ""

		self.compiler = compiler
		self.ref_compiler = ref_compiler
		self.filepath = filepath
		self.basename = os.path.basename(filepath)

	def __str__(self):
		output = "%s: " %self.basename
		if self.result == 1:
			output+=("OK")
			return output
		output += "ERROR\n"

		output +=self.ref_compilator_output
		output +=self.compilator_output
		output +=self.differ_output
		return output


	def test(self):
		if not self._compile_reference():
			self.result = 0
			return

		if not self._compile():
			self._diff()
			self.result = 0
		else:
			if self._diff():
				self.result = 1
			else:
				self.result =0

	def _compile_reference(self):
		try:
			self.ref_compiler.compile(self.filepath)
			self._save_reference_log_file()
			return True
		except CompileException as e:
			self.ref_compilator_output = "reference compilation failed:\n\t%s\n" %str(e)
			return False
		except TimeoutException as e:
			self.ref_compilator_output = "reference compilation failed:\n\t%s\n" %str(e)

	def _save_reference_log_file(self):
		directory = os.path.dirname(self.filepath) + '/'
		file_basename = self.basename.split(".cflat")[0]
		os.rename(directory+file_basename + ".log",directory+file_basename + ".ref.log")		
		
	def _compile(self):
		try:
			self.compiler.compile(self.filepath)
			return True
		except TimeoutException as e:
			self.compilator_output = "\tCompilator:\n\t\t%s\n" %str(e)
			return False
		except CompileException as e:
			self.compilator_output = "\tCompilator:\n\t\t%s\n" %str(e)
			return False

	def _diff(self):
		try:
			LogDiffer.diff(self.filepath)
			return True
		except CompareException as e:
			self.differ_output = '\tLogFile differ:\n\t\t'+str(e)
			return False

class Compiler():
	compile_timeout = 5
	def __init__(self,compiler_path):
		self.compile_cmd = 'java -jar ' + compiler_path + ' -testparser '
		
	def compile(self,filepath):
		def target():
			cmd = self.compile_cmd + filepath
			self.process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,\
				stderr=subprocess.PIPE)
			self.err_out = (self.process.communicate()[1].decode('utf-8'))

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

class LogDiffer():

	def diff(filepath):
		basename = os.path.basename(filepath)
		file_basename = basename.split(".cflat")[0]
		full_path = os.path.dirname(filepath) + '/' + file_basename
		try:
			exp_file = open(full_path + '.ref.log','r')
			act_file = open(full_path + '.log','r')
		except Exception as e:
			raise CompareException("no diffing performed: %s" %str(e))

		LogDiffer._compare(exp_file,act_file,file_basename+".log")

	def _compare(exp_file,act_file,basename):
		exp_line = ""
		act_line = ""
		act_line_number = 0
		for act_line in act_file:
			act_line_number += 1
			if act_line.startswith('Parser:'):
				while not exp_line.startswith("Parser:"):
					exp_line = exp_file.readline()
				exp_line = exp_line.split("Parser:")[1].strip()
				act_line = act_line.split("Parser:")[1].strip()
				if not exp_line == act_line:
					exp_file.close()
					act_file.close()
					raise CompareException("%s expected, but found %s on line number %d in %s"\
						%(exp_line,act_line,act_line_number,basename))
		exp_file.close()
		act_file.close()


test = CompileTester()