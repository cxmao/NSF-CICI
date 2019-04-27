# Author: Christina Mao
# Date Created: 04-25-2019
# Description:Takes HTM results files and evaluate results to get confusion matrix.
# Assumes rest of system background is free from attacks
#
#---------------------------------------------------------------------------------
from __future__ import division
import os
import csv
import collections
import re


ATTACK_LOG = "/home/cmao/Repos/nsf-cici/data/test/attack_test.csv"
RESULT_DIR = "/home/cmao/Repos/nsf-cici/data/test/results"
EVAL_DIR = "/home/cmao/Repos/nsf-cici/data/test/results/eval"

def CheckPath(dirpath):
	if not os.path.isdir(dirpath):
		os.makedirs(dirpath)

def validatepath(dirpath):
	try:
		resultfiles = []
		if os.path.isdir(dirpath):
			for r, d, f in os.walk(dirpath):
				for file in f:
					resultfiles.append(os.path.join(r,file))
	except:
		print(dirpath + " is not a directory")
	return resultfiles



def GetAttackWindows(nestdict):
	"""
	Description:
	:param nestdict:
	:return:
	"""
	print "Getting attack windows"
	atkDict = atkRecord = {}
	windowCnt = atkCount = 0
	for key in nestdict:
		if (nestdict[key]["attack"] == str(1)):
			atkCount +=1
			atkRecord[key] = nestdict[key]["anomaly_level"]
		elif(nestdict[key]["attack"] == str(0) and atkCount > 0): # Reset counter
			atkDict[windowCnt] = atkRecord
			print atkDict[windowCnt]
			atkRecord.clear()
			atkCount = 0
			windowCnt += 1
	#print atkDict
	return atkDict

def GetTPRWindowed(nestdict):
	"""
	Description:
	:param nestdict:
	:return:
	"""
	print("Getting True Positive Rate")
	TPRwin = 0
	# Get window of continuous attack

	return TPRwin

# Get True Positive Rate (TPR) Sensitivity
def GetTPR(nestdict):
	print("Getting True Positive Rate")
	TP = TN = FP = FN = TPR = 0
	for key in nestdict:
		anomLvl = nestdict[key]["anomaly_level"]
		attackVal = nestdict[key]["attack"]

		if(anomLvl == 'HIGH' and attackVal == str(1)): # Hit
			TP = TP + 1
			print anomLvl, attackVal,  "TP", TP
		elif(anomLvl != 'HIGH' and attackVal == str(1)): # Miss
			FN = FN + 1
			print anomLvl, attackVal, "FN", FN
		elif(anomLvl == 'HIGH' and attackVal == str(0)): # False Alarm
			FP = FP + 1
			print anomLvl, attackVal, "FP", FP

		else:#(anomLvl != 'HIGH' and attackVal == str(0)): # True Negative
			TN = TN + 1
			print anomLvl, attackVal, "TN", TN

	P = TP + FN
	N = TN + FP


	print P, N
	print TP, FP, TN, FN

	TPR = TP/P
	FPR = FP/N
	TNR = TN/N
	FNR = FN/P

	return TPR, FPR, TNR, FNR

# Get True Negative Rate (TNR) Specificity
def GetTNR():

	return

# Get False Positive Rate (FPR) Fall-out
def GetFPR():
	return
# Get False Negative Rate (FNR) Miss-rate
def GetFNR():
	return




def CSVtoDict(resultspath, attackpath):
	'''
	Description: Takes HTM Studio results CSV and turns it into a dictionary of dictionary
	with timestamp as key. Appends attack value to nested dictionary.
	:param resultspath: Full path to HTM Studio CSV results
	:param attackpath: Full path to timestamped attack log CSV
	:return: <nested dictionary> key: timestamp value: <innerdictionary>
			<inner dictionary>	key: metricname value: metric value
	'''
	orderedDict = collections.OrderedDict()

#	nestedDict = {}
	with open(resultspath, 'r') as resultsfile:
		resultsRows = csv.DictReader(resultsfile, delimiter = ',')
		for row in resultsRows:
			innerdict = {}
			timestamp = row["timestamp"]
			for ind, key in enumerate(row):
				if not (key == "timestamp"):
					innerKey = key
					innerVal = row[key]
					innerdict[innerKey] = innerVal
#			print innerdict
#			nestedDict[row["timestamp"]] = innerdict
			orderedDict[timestamp] = innerdict

	#Append Attack log to nested dictionary
	with open(attackpath, 'r') as attacklog:
		attackRows = csv.DictReader(attacklog, delimiter = ',')
		for row in attackRows:
			attackTime = row["timestamp"]
			attackValue = row["attack"]
			if attackTime in orderedDict:
				orderedDict[attackTime]["attack"] = attackValue
#				print attackTime
#				print orderedDict[attackTime]
#	print nestedDict
#	print orderedDict
	return orderedDict


def main():
	# Gene
	# Check that file exists
	# Get all results files
	resultfiles = validatepath(RESULT_DIR)
	CheckPath(EVAL_DIR)
	print resultfiles
	for aFile in resultfiles:
		data = CSVtoDict(aFile, ATTACK_LOG)
		origFName = re.search("(csv)", aFile) #fix
		outFileName = EVAL_DIR + origFName.group(0)  + "_matrix.txt"
		evalFile = open(outFileName, "w+" )
		evalWriter = csv.writer(evalFile)
		results = GetTPR(data)
		print results

		# Get Windowed Results
#		atkWindows = GetAttackWindows(data)
#		print atkWindows
		#evalWriter.writerow(TPR) # expects a list

	return


if __name__ == "__main__":
	main()