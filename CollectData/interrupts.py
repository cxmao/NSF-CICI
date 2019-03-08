"""
Author: Christina Mao 
Date Created: 03-06-2019 
Description: Read /proc/ file system  and parses to a time-stamped csv file
http://nupic.docs.numenta.org/1.0.3/quick-start/example-data.html 

"""
import os
import time 
import csv
import sys, signal # Handle CTRL-C
from datetime import datetime
from datetime import date

__PROC_PATH = "/proc/interrupts"
__FILE_NAME = str(date.today()) + "_interrupts.csv"
__OUTPUT_PATH = "/home/cmao/Repos/nsf-cici/data/procfs/interrupts"

def signal_handler(signal, frame):
	print("\n Program exiting..")
	sys.exit(0)

def main(): 
	"""
	Description:  Takes /proc/interrupts and writes/appends to a file labeled with today's date
	Parameters: 
	Returns:
	"""
	# Handle graceful shutdown from CTRL-C or Kill 
	signal.signal(signal.SIGINT, signal_handler)

	# Check if output path exists 
	if not os.path.exists(__OUTPUT_PATH):
		os.mkdir(__OUTPUT_PATH)
	os.chdir(__OUTPUT_PATH)		
	writeFile = open(__FILE_NAME, "a")
	while True :
		# Read Proc Filesystem File 
		with open(__PROC_PATH) as file: 
			# Get timestamp 
			ts = datetime.now()
			ts = ts.strftime("%Y-%m-%d %H:%M:%S")
			writer = csv.writer(writeFile)
			# Format as a time-stamped csv file 
			for line in file:
				formattedLine = line.split()
				formattedLine.insert(0,str(ts))
				writer.writerow(formattedLine)
		# Wait for 1s
		time.sleep(1)

	print ("Results written to " + __OUTPUT_PATH)
	file.close()
	return 


if __name__ == "__main__":
	main()