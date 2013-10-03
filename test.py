#!/usr/bin/env python3
import sys
import subprocess
import os

compiler_path = '../Cflat.jar'
compile_cmd = 'java -jar ' + compiler_path + ' -testparser '
testfiles_dir = './testfiles/'
output_dir = './output/'

#cleans the outfolder for .log and .s files
#if no argument is provided, the script will try to compile all cflat files in the testfolder
#if a argument is provided, the script will try to compile the file provided
def main():
	clean(output_dir)

	if(len(sys.argv)>1):
		if(sys.argv[1].endswith('/')):
			compile_files(get_cflat_files(sys.argv[1]))
			clean(testfiles_dir)
		else:
			compile_files([sys.argv[1]]) 
			save_log_files(sys.argv[1])
	else:
		compile_files(get_cflat_files(testfiles_dir))
		clean(testfiles_dir)

#Compile all files in paths list
def compile_files(paths):
	for file_path in paths:
		cmd = compile_cmd + file_path
		cflat_compile_process = subprocess.Popen(cmd.split(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
		
		output = cflat_compile_process.communicate()
		returncode = cflat_compile_process.returncode

		if returncode != 0:
			on_error(file_path,output[0],output[1],cmd)

#Prints an error message to the console.
#Removes all unwanted .log and .s files
def on_error(filepath,output,error_output,compile_cmd):
	_dir,basename = os.path.split(filepath)
	print("ERROR while compiling %s" %(basename))
	print("Compiled with the command: " + compile_cmd)
	print("____________________________________")
	print(output)
	print(error_output)

	save_log_files(_dir+'/')
	clean(_dir+'/')
	exit()

#moves .log and .s files to outfolder
def save_log_files(_dir):
	filelist = [ f for f in os.listdir(_dir) if f.endswith(".log") or f.endswith(".s")]
	for f in filelist:
		os.rename(_dir + f,output_dir+f)

#removes all .log and .s files
def clean(_dir):
	filelist = [ f for f in os.listdir(_dir) if f.endswith(".log") or f.endswith(".s")  ]
	for f in filelist:
		os.remove(_dir +f)

#Retrives all cflat files in dir
def get_cflat_files(dir_path):
	filelist = [ dir_path + f  for f in os.listdir(dir_path) if f.endswith(".cflat")]
	return filelist

main()
