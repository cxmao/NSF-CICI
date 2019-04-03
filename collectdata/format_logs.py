# Author: Christina Mao
# Date Created: 04-02-2019
# Description:Process input data from /proc filesystem to feed into NuPic Framework
# See: http://nupic.docs.numenta.org/1.0.0/quick-start/example-data.html
# TO-DO: Add argument Parsing
#---------------------------------------------------------------------------------
from __future__ import division
from datetime import datetime
import argparse
import os
import re
import csv
import collections  # To sort dictionaries


#Set filedate
FILEDATE = "2019-04-02"

#Set ProcFS data log directory paths
STATDIR = "/home/cmao/Repos/nsf-cici/data/procfs/stat/"
NETDIR = "/home/cmao/Repos/nsf-cici/data/procfs/net/"
OUTDIR = "/home/cmao/Repos/nsf-cici/data/clean/procfs/"


def GetInterrupts(filename):
	"""
	Description: Get Interrupts from /proc/stat and
				return a dictionary with timestamps as key
	Parameters:
		filename <string>:  /procfs log filename
	Return:
		interruptsDict <dict>: timestamp, #interrupts since boot
	"""
	file = open(STATDIR + filename, "r")
	interruptsDict={}
	for line in file: 
		if (re.search("intr", line)):
			elements = line.split(",")
			interruptsDict[elements[0]] = int(elements[2])
	return interruptsDict


def GetContext(filename):
	"""
	Description: Get Context Switches from /proc/stat
				and return a dictionary with date timestamp as key
	Parameters:
		filename <string>
	Return:
		contextDict <string> - timestamp, #total context switches since boot
	"""
	file = open(STATDIR + filename, "r")
	contextDict={}
	for line in file:
		if (re.search("ctxt", line)):
			elements = line.split(",")
			contextDict[elements[0]] = int(elements[2])  #.strip("\r\n")
	return contextDict


def GetBytes(filename):
	"""
	Description: Get total Packets & Bytes TXed/RXed from /proc/net/dev
				and return as a dictionary with list as values
	Parameters:
		filename <string>
	Return:
		netDict <dictionary> : <key> timestamp,
								<list> total Bytes Rxed,
									total Bytes Txed,
									total Packets Rxed,
									total Packets Txed
	"""
	file = open(NETDIR + filename, "r")
	bytesDict = {}
	RxBytes = TxBytes = RxPkts = TxPkts = 0

	for line in file:
		elements = line.split(",")
		# Reset counter on loopback
		if(elements[1] == 'lo:'):
			# Write previously stored values
			if(bool(bytesDict) and elements[1] != tstamp):
				bytesDict[tstamp] = [RxBytes, TxBytes, RxPkts, TxPkts]
			# Get new timestamp  and reset counters
			tstamp = elements[0]
			RxBytes = int(elements[2])
			TxBytes = int(elements[10])
			RxPkts = int(elements[3])
			TxPkts = int(elements[11])
			bytesDict[tstamp] = ''  #Hacky
		else:
			RxBytes += int(elements[2])
			TxBytes += int(elements[10])
			RxPkts += int(elements[3])
			TxPkts += int(elements[11])
	return bytesDict


def GetMetrics(numdict, denomdict, csvwriter):
	row = []
	for key in numdict:
		try:
			if key in denomdict:
				row.extend((key, numdict[key]))  # Append sequence
				for v in range(0, len(denomdict[key])):
					temp = float(numdict[key]/denomdict[key][v])
					row.append('%.5f' % temp)
				csvwriter.writerow(row)
				del row[:]  # Clear list
		except IndexError:
			pass


def DirExists(dirpath):
	if(not os.path.exists(dirpath)):
		os.makedirs(dirpath)


def FileExists(filepath):
	exists = os.path.isfile(filepath)
	if exists:
		#Extract date
		FILEDATE = re.search(r'\d{4}-\d{2}-\d{2}', filepath)
		print(FILEDATE)


def main(): 
	
	"""
	# Argument parsing from command-line
	parser = argparse.ArgumentParser(description='Provide dates of logs: startdate enddate metric')
	parser.add_argument('Filedate', metavar='F', type=argeparse.FileType('r'), help='Date of file as specified in /data/proc/')
	parser.add_argument('Outputdirectory', metavar='O', type=string, help='Absolute directory path to store logs')
	args = parser.parse_args()
 	"""
 
	# Check file directory paths exist 
	DirExists(OUTDIR)
	#FileExists(STATDIR + FILEDATE + "_stat.csv")
	#FileExists(NETDIR + FILEDATE + "_net.csv")

	# Get Dictionaries
	interrupts = GetInterrupts(FILEDATE + "_stat.csv")
	context = GetContext(FILEDATE + "_stat.csv")
	net = GetBytes(FILEDATE + "_net.csv")


	# Sort Dictionaries
	intDict = collections.OrderedDict(sorted(interrupts.items()))
	contDict = collections.OrderedDict(sorted(context.items()))
	netDict = collections.OrderedDict(sorted(net.items()))

	"""
	 Process dictionaries to get metrics:
		IBR = Interrupts/Bytes Received
		IBT = Interrupts/Bytes Transferred
		IPR = Interrupts/Packets Received
		IPR = Interrupts/Packets Transferred
		CBT = Context Switch/Bytes Transferred
		CBR = Context Switch/Bytes Received
		CPT =  Context Switch/Packets Transferred
		CPR = Context Switch/Packets Received
	"""

	# Prepare csv writers to output in NuPic input format 
	# See: http://nupic.docs.numenta.org/1.0.0/quick-start/example-data.html)
	interruptOutput = open(OUTDIR + FILEDATE + '_interrupts_nupic.csv', 'wb')
	interruptWriter = csv.writer(interruptOutput, delimiter=',')
	contextOutput = open(OUTDIR + FILEDATE + '_context_nupic.csv', 'wb')
	contextWriter = csv.writer(contextOutput, delimiter=',')
	intHeader = [
					"Timestamp",
					"Total Interrupts",
					"IBR",
					"IBT",
					"IPR",
					"IPT"
				]
	fieldTypes = [
				"datetime",
				"int",
				"float",
				"float",
				"float",
				"float",
				]
	flags = ["T", "C", "C", "C", "C", "C"]
	interruptWriter.writerow(intHeader)
	interruptWriter.writerow(fieldTypes)
	interruptWriter.writerow(flags)

	contheader = [
					"Timestamp",
					"Total Context Switches", 
					"CBR",
					"CBT",
					"CPR",
					"CPT"
				]
	contextWriter.writerow(contheader)
	contextWriter.writerow(fieldTypes)
	contextWriter.writerow(flags)

	#Get Metrics
	GetMetrics(intDict, netDict, interruptWriter)
	GetMetrics(contDict, netDict, contextWriter)

if __name__ == '__main__':
	main()
