# Author: Christina Mao 
# Date: 04-10-2019 
# Description: Read logs and copy portion with date to new file 
import csv
import re 

DIRPATH = '/home/cmao/Repos/nsf-cici/data/hping04062019/procfs/clean/'
INFILE = '2019-04-05_context_clean.csv'
DATE =  '2019-04-06'
OUTFILE = '_context_clean.csv'

def main():
	
	outFile = open(DIRPATH + DATE + OUTFILE, 'wb')

	with open(DIRPATH + INFILE, 'r') as f: 
		# Write header 
		first_line = f.readline() 
		type_line = f.readline()
		flags_line = f.readline()
		outFile.write(first_line)
		outFile.write(type_line)
		outFile.write(flags_line)
		# Search for date
		for line in f: 

			if(re.search(r''+ re.escape(DATE), line, re.IGNORECASE)):
				outFile.write(line)
	outFile.close()


if __name__ == '__main__':
	main()