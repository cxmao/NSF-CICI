# Author: Christina Mao
# Date Created: 04-02-2019
# Description:Process input data from /proc filesystem to feed into NuPic Framework
# See: http://nupic.docs.numenta.org/1.0.0/quick-start/example-data.html
# TO-DO: Add argument Parsing
#---------------------------------------------------------------------------------
from __future__ import division
from datetime import datetime
from datetime import timedelta
from dateutil.parser import parse
import argparse
import os
import re
import csv
import collections  # To sort dictionaries
from operator import sub

ROOTDIR = "/home/cmao/Repos/nsf-cici/data/experiment1/"

#Set filedate
FILEDATE = "2019-04-24"
# Set Input (Raw ProcFS logs) directory
STATDIR = ROOTDIR + "/procfs/raw/"
NETDIR = ROOTDIR + "/procfs/raw/"
# Set Output directory
OUTDIR = ROOTDIR + "/procfs/clean/"


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
	interruptsDict = {}
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
		if(re.search("ctxt", line)):
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

	tstamp = 0
	for line in file:
		elements = line.split(",")
		# Data check 
		if(len(elements) != 18):
			pass
		# Reset counter on new timestamp
		elif(tstamp != elements[0]):
			if(bool(bytesDict) and elements[1] != tstamp):
				bytesDict[tstamp] = [RxBytes, TxBytes, RxPkts, TxPkts]
			# Get new timestamp  and reset counters
			tstamp = elements[0]
			RxBytes = int(elements[2])
			TxBytes = int(elements[10])
			RxPkts = int(elements[3])
			TxPkts = int(elements[11])
			bytesDict[tstamp] = '' # Hacky
		else:
			RxBytes += int(elements[2])
			TxBytes += int(elements[10])
			RxPkts += int(elements[3])
			TxPkts += int(elements[11])

	return bytesDict


def GetMetrics(numdict, denomdict, csvwriter):
	print len(numdict)
	print len(denomdict)
	row = []
	numkeys = sorted(numdict.keys()) # to access index
	prevTimestamp = "2000-01-01 00:00:00"
	for index, key in enumerate(numkeys):
		try:
			"""
			print("index", index)
			print("keylist[index]", keylist[index])
			print("key", key)
			print("dict[key]", numdict[key])
			print("Value",numdict[keylist[index]])
			print("Value",numdict[key])
			"""
			prevkey = numkeys[index -1]
			# Skip first row because we can't get previous value to calculate from
			if(index > 0 and prevkey in denomdict):
				prevInt = numdict[prevkey]
				prevBytes = denomdict[prevkey]

			# Match by timestamp and check for 1s diff
			tsdelta = datetime.strptime(prevTimestamp, '%Y-%m-%d %H:%M:%S') - datetime.strptime(key, '%Y-%m-%d %H:%M:%S')
			print tsdelta
			if(index > 0 and key in denomdict and len(denomdict[key]) == 4):
				# Get Bytes/Packets Rxed and Txed per second
				currBytes = denomdict[key]
				print "prev" + str(prevBytes)
				print "curr" + str(currBytes)
				bytesPs = map(lambda x, y: abs(x - y), prevBytes, currBytes)
				print "ps" + str(bytesPs)
				if(tsdelta.total_seconds() == -1.0):
						# Get Total Interrupts/Context Switches
						row.extend((key, numdict[key]))  # Append sequence
						# Get interrupts/Context Switches per second
						currInt = numdict[key]
						intPs = abs(currInt - prevInt)
						row.append(intPs)

						# Get Interrupts/Context Switches Ratio w Bytes/Packets
						for v in range(0, len(bytesPs)):
							ratio = float(bytesPs[v]/intPs)
							row.append('%.5f' % ratio)
						csvwriter.writerow(row)
						del row[:]  # Clear list
			prevTimestamp = key
		except IndexError or KeyError:
			pass
	return


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
	#print interrupts
	context = GetContext(FILEDATE + "_stat.csv")
	net = GetBytes(FILEDATE + "_net.csv")


	# Sort Dictionaries
	intDict = collections.OrderedDict(sorted(interrupts.items()))
	contDict = collections.OrderedDict(sorted(context.items()))
	netDict = collections.OrderedDict(sorted(net.items()))

	"""
	 Process dictionaries to get metrics:
	 	# Interrupts Clean
		IBR = Interrupts/Bytes Received
		IBT = Interrupts/Bytes Transferred
		IPR = Interrupts/Packets Received
		IPR = Interrupts/Packets Transferred
		BTI = Context Switch/Bytes Transferred
		BRI = Context Switch/Bytes Received
		PTI =  Context Switch/Packets Transferred
		PRI = Context Switch/Packets Received

		# Context Clean
		CBT = Context Switch/Bytes Transferred
		CBR = Context Switch/Bytes Received
		CPT =  Context Switch/Packets Transferred
		CPR = Context Switch/Packets Received

		BTC = Context Switch/Bytes Transferred
		BRC = Context Switch/Bytes Received
		PTC =  Context Switch/Packets Transferred
		PRC = Context Switch/Packets Received
	"""

	# Prepare csv writers to output in NuPic input format 
	# See: http://nupic.docs.numenta.org/1.0.0/quick-start/example-data.html)
	interruptsFile = OUTDIR + FILEDATE + '_interrupts_clean.csv'
	interruptOutput = open(interruptsFile, 'wb')
	interruptWriter = csv.writer(interruptOutput, delimiter=',')

	contextFile = OUTDIR + FILEDATE + '_context_clean.csv'
	contextOutput = open(contextFile, 'wb')
	contextWriter = csv.writer(contextOutput, delimiter=',')
	intHeader = [
					"timestamp",
					"Total Interrupts since Boot",
					"Interrupts per Second",
					"IBR",
					"IBT",
					"IPR",
					"IPT"
				]
	fieldTypes = [
				"datetime",
				"int",
				"int",
				"float",
				"float",
				"float",
				"float",
				]
	flags = ["T", "C", "C", "C", "C", "C", "C"]
	interruptWriter.writerow(intHeader)
	interruptWriter.writerow(fieldTypes)
	interruptWriter.writerow(flags)
	
	contheader = [
					"timestamp",
					"Total Context Switches since Boot", 
					"Contect Switches per Second",
					"CBR",
					"CBT",
					"CPR",
					"CPT"
				]
	contextWriter.writerow(contheader)
	contextWriter.writerow(fieldTypes)
	contextWriter.writerow(flags)

	# Get Metrics
	GetMetrics(intDict, netDict, interruptWriter)
	print ("Results  written to " + interruptsFile)
	GetMetrics(contDict, netDict, contextWriter)
	print ("Results  written to " + contextFile)

if __name__ == '__main__':
	main()
