#!/usr/bin/env python3
import sys
import subprocess
import os
import argparse

dirname = os.path.dirname(sys.argv[0])
compiler_path = dirname + '/../Cflat.jar'
testfiles_dir = dirname + '/testfiles/'
output_dir = dirname + '/output/'

compile_cmd = 'java -jar ' + compiler_path + ' -testparser '

def main():
	args = parse_args()
	init_output_folder()
	if args.dir.endswith('/'):
		compile_files(get_cflat_files(args.dir))
		save_log_files(args.dir)
	else :
		compile_files([args.dir])
		save_log_files(os.path.dirname(args.dir)+'/')

def parse_args():
	parser = argparse.ArgumentParser(description='automate your compile testing')
	parser.add_argument('dir', nargs='?', default=testfiles_dir,help='optionaly specify a file or folder to test')
	return parser.parse_args()


#Compile all files in paths list
def compile_files(paths):
	for filepath in paths:
		cmd = compile_cmd + filepath

		cflat_compile_process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		
		error_output = cflat_compile_process.communicate()[1]
		returncode = cflat_compile_process.returncode

		print("\n---------------------------------------------------------------")
		
		if returncode != 0:
			on_error(filepath,error_output,cmd)

		else :
			print("%s: OK" %os.path.basename(filepath))

def on_error(filepath,error_output,compile_cmd):
	_dir,basename = os.path.split(filepath)
	print("%s: ERROR" %(basename))
	print("Output:")
	print("\t"+str(error_output))

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


main()
