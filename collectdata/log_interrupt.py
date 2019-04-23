"""
Author: Christina Mao
Date Created: 03-06-2019
Description: Reads /proc/interrupts and logs to a time-stamped csv file
http://nupic.docs.numenta.org/1.0.3/quick-start/example-data.html 
"""
from datetime import datetime
from datetime import date
import os
import time
import csv
import sys, signal  # Handle CTRL-C


__PROCPATH = "/proc/interrupts"
__FILE_NAME = str(date.today()) + "_interrupts.csv"
__OUTPATH = "/var/log/procfs/"


def signal_handler(signal, frame):
	print("\n Program exiting..")
	sys.exit(0)


def log_data(procpath, filename, outpath):
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
			filename = str(log_date) + "_interrupts.csv"
			writeFile = open(filename, "a")
			writeFile.write("\n")
		# Read Proc FS File
		with open(procpath) as file:
			# Get timestamp
			ts = datetime.now()
			ts = ts.strftime("%Y-%m-%d %H:%M:%S")
			writer = csv.writer(writeFile)
			# Format as a time-stamped csv file
			for line in file:
				formattedLine = line.split()
				formattedLine.insert(0, str(ts))
				writer.writerow(formattedLine)
		# Wait for 1s
		time.sleep(1)
	writeFile.close()
	print("Results written to " + outpath)


def main():
	"""
	Description:  Takes /proc/interrupts and writes/appends to a file for one day.
	Returns:
	"""
	# Handle graceful shutdown from CTRL-C or Kill
	signal.signal(signal.SIGINT, signal_handler)

	log_data(__PROCPATH, __FILE_NAME, __OUTPATH)

	return 0


if __name__ == "__main__":
	main()
