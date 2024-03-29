"""
Author: Christina Mao
Date Created: 03-06-2019
Description: Reads /proc/net/dev and logs to a time-stamped csv file
http://nupic.docs.numenta.org/1.0.3/quick-start/example-data.html

"""
from datetime import datetime
from datetime import date
import os
import time
import csv
import re
import sys, signal  # Handle CTRL-C


__PROCPATH = "/proc/net/dev"
__FILE_NAME = str(date.today()) + "_net.csv"
__OUTPATH = "/var/log/procfs/"


def signal_handler(signal, frame):
	print("\n Program exiting..")
	sys.exit(0)


def is_data(inputstring):
	"""
	Description: Checks if string is not a header line.
        Checks if string contains digits.
		@inputstringr <string> - string to check
	Returns:
		<bool>
	"""
	return bool(re.search(r'\d', inputstring))


def log_data(procpath, filename, outpath):
	"""
	Description:  Takes /proc/interrupts and writes/appends to a file for one day.
	Returns:
	"""
	# Check if output directory exists
	if(not os.path.exists(outpath)):
		os.makedirs(outpath)
	os.chdir(outpath)
	# Create log file
	writeFile = open(filename, "a") 
	writeFile.write("\n")
	log_date = date.today()
	while True:
		# Check date and create new log file for new date
		if(date.today() != log_date):
			log_date = date.today()
			# Create new log file
			filename = str(log_date) + "_net.csv"
			writeFile = open(filename, "a")
			writeFile.write("\n")
		# Read Proc Filesystem File 
		with open(procpath) as file:
			# Get timestamp 
			ts = datetime.now()
			ts = ts.strftime("%Y-%m-%d %H:%M:%S")
			writer = csv.writer(writeFile)
			# Format as a time-stamped csv file
			for line in file:
				if(is_data(line)):
					formattedLine = line.split()
					formattedLine.insert(0, str(ts))
					writer.writerow(formattedLine)
		# Wait for 1s
		time.sleep(1)
	writeFile.close()
	print("Results written to " + outpath)


def main(): 
	# Handle graceful shutdown from CTRL-C or Kill
	signal.signal(signal.SIGINT, signal_handler)
	log_data(__PROCPATH, __FILE_NAME, __OUTPATH)
	return 0


if __name__ == "__main__":
	main()
