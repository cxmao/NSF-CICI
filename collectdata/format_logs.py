# Author: Christina Mao 
# Date Created: 04-02-2019 
# Description:Process input data from /proc filesystem to feed into NuPic Framework  (See: http://nupic.docs.numenta.org/1.0.0/quick-start/example-data.html)
from __future__ import division
import argparse 
import os 
import re
import csv
from datetime import datetime
import collections #To sort dictionaries


#Set filedate
FILEDATE = "2019-04-02"

#Set ProcFS data log directory paths
STAT = "/home/cmao/Repos/nsf-cici/data/procfs/stat/"
NET = "/home/cmao/Repos/nsf-cici/data/procfs/net/"



def GetInterrupts(filename):
	"""
	Description: Get Interrupts from /proc/stat and return a dictionary with date timestamps as key
	Parameters: 
		filename <string>: 
	Return:
		interruptsDict <dict>: timestamp, #interrupts since boot

	"""
	file = open(STAT + filename, "r")
	interruptsDict={}
	for line in file: 
		if (re.search("intr", line)):
			elements = line.split(",")
			interruptsDict[elements[0]] = int(elements[2])
	#print interruptsDict
	return interruptsDict


def GetContext(filename):
	"""
	Description: Get Context Switches from /proc/stat and return a dictionary with date timestamp as key
	Parameters:
		filename <string>
	Return:
		contextDict <string> - timestamp, #context switches since boot 
	"""
	file = open(STAT + filename, "r")
	contextDict={}
	for line in file: 
		if (re.search("ctxt", line)):
			elements = line.split(",")
			contextDict[elements[0]] = int(elements[2]) #.strip("\r\n")
	#print  contextDict
	return contextDict


def GetBytes(filename):
	"""
	Description: Get total Packets & Bytes TXed/RXed from /proc/net/dev and return as a dictionary with list as values
	Parameters:
		filename <string>
	Return:
		netDict <dictionary> : <key> timestamp, <list> total Bytes Rxed, total Bytes Txed, total Packets Rxed, total Packets Txed
	"""
	file = open(NET + filename, "r")
	bytesDict={}
	RxBytes = TxBytes= RxPkts = TxPkts = 0

	for line in file:
	#	print line
		elements = line.split(",")
		#Reset counter on loopback 
		if(elements[1] == 'lo:'):
			#Write previously stored values
			if( bool(bytesDict) and elements[1] != tstamp):
				bytesDict[tstamp] = [RxBytes,TxBytes, RxPkts, TxPkts]
			#Get new timestamp  and reset counters
			#tstamp =  datetime.strptime(elements[0], '%Y-%m-%d %H:%M:%S')
			tstamp = elements[0]
			RxBytes =  int(elements[2])
			TxBytes = int(elements[10])
			RxPkts = int(elements[3])
			TxPkts = int(elements[11])
			bytesDict[tstamp] = ''
		else:
			RxBytes += int(elements[2])
			TxBytes += int(elements[10])
			RxPkts += int(elements[3])
			TxPkts += int(elements[11])
	return bytesDict


def main(): 
	parser = argparse.ArgumentParser(description ='Provide dates of logs: startdate enddate metric')
	parser.parse_args()
 
	# Get Dictionaries
	interrupts = GetInterrupts(FILEDATE + "_stat.csv")
	context = GetContext(FILEDATE + "_stat.csv")
	net = GetBytes(FILEDATE + "_net.csv")


	# Sort Dictionaries
	intDict = collections.OrderedDict(sorted(interrupts.items()))
	contDict = collections.OrderedDict(sorted(context.items()))
	netDict = collections.OrderedDict(sorted(net.items()))


	# Write results to csv file in nupic input format 
	# See: http://nupic.docs.numenta.org/1.0.0/quick-start/example-data.html)
	interruptOutput = open('../data/int_out.csv', 'wb') 
	interruptWriter = csv.writer(interruptOutput, delimiter = ',') 
	contextOutput = open('../data/cont_out.csv', 'wb') 
	contextWriter = csv.writer(contextOutput, delimiter = ',') 
	#TO-DO: Write header and datatype 
	#interruptWriter.writerow()


		# Convert time to datetime type

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
	for key in intDict:
		try:
			if key in netDict:
				IBR = float(intDict[key]/netDict[key][0])
				IBT = float(intDict[key]/netDict[key][1])
				IPT = float(intDict[key]/netDict[key][2])
				IPR = float(intDict[key]/netDict[key][3])

				print key, intDict[key], netDict[key], "\n"
				print '%.5f' % IBR, '%.5f' %IBT, '%.5f' % IPT, '%.5f' % IPR
				row = key 
				"""
						+ '%.5f' % IBR + ","
						+ '%.5f' % IBT + ","
						+ '%.5f' % IPT + "," 
						+ '%.5f' % IPR
				"""
				interruptWriter.writerow(row)
		except IndexError: 
			pass

	#To-Do: Context Switch 
	for key in contDict:
		try: 
			if key in netDict: 
				CBR = float(contDict[key]/netDict[key][0])
				CBT = float(contDict[key]/netDict[key][1])
				CPT = float(contDict[key]/netDict[key][2])
				CPR = float(contDict[key]/netDict[key][3])
		except IndexError:
			pass


if __name__ == '__main__':
	main()