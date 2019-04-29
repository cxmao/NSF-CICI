# Author: Christina Mao
# Date Created: 04-25-2019
# Description:Takes HTM results files and evaluate results to get confusion matrix.
# Assumes rest of system background is free from attacks
#
#---------------------------------------------------------------------------------
from __future__ import division
import os
import csv
import re

ATTACK_LOG = "/home/cmao/Repos/nsf-cici/data/test/attack_test.csv"
RESULT_DIR = "/home/cmao/Repos/nsf-cici/data/test/results/"
EVAL_DIR = "/home/cmao/Repos/nsf-cici/data/test/eval/"

def directory_exists(dirpath):
	"""
	Description: Check that a directory path exists
	:param dirpath: <string> Full directory path
	:return: null
	"""
	if not os.path.isdir(dirpath):
		os.makedirs(dirpath)


def get_directory_files(dirpath):
	"""
	Description: Given a directory path, get a list of all files in directory 
	:param dirpath <string> Full directory path
	:return: dirFiles: <list> list of file paths in directory
	"""
	try:
		dirFiles = []
		if os.path.isdir(dirpath):
			for r, d, f in os.walk(dirpath):
				for file in f:
					dirFiles.append(os.path.join(r,file))
	except:
		print(dirpath + " is not a directory")
	return dirFiles


def get_accuracy(Tpos, Fpos, Tneg, Fneg):
	"""
	Description: Get accuracy of results
	:param Tpos: <int> Number of true positives
	:param Fpos: <int> Number of false positives
	:param Tneg: <int> number of true negatives
	:param Fneg: <int> Number of false negatives
	:return: accuracy: <float> Accuracy
	"""
	pos = Tpos + Fneg
	neg = Tneg + Fpos
	accuracy = (Tpos + Tneg) / (pos + neg)
	return accuracy


def get_matching_matrix(Tpos, Fpos, Tneg, Fneg):
	"""
	Description: Get matching matrix (aka confusion matrix)
	:param Tpos: <int> Number of true positives
	:param Fpos: <int> Number of false positives
	:param Tneg: <int> number of true negatives
	:param Fneg: <int> Number of false negatives
	:return: <tuple>: TPR: <float> True positive rate, FPR <float> False positive rate,
	 				 TNR: <float> True negative rate, FNR <float> False negative rate
	"""
	pos = Tpos + Fneg
	neg = Tneg + Fpos
	
	TPR = Tpos / pos  # True Positive Rate (TPR) Sensitivity
	FPR = Fpos / neg  # False Positive Rate (FPR) Fall-out
	TNR = Tneg / neg  # True Negative Rate (TNR) Specificity
	FNR = Fneg / pos  # False Negative Rate (FNR) Miss-rate

	return TPR, FPR, TNR, FNR

def get_windowed_data(datadict):
	"""
	Description: Process results data into windowed intervals
	:param datadict: <dict>Nested dictionary returned from @results_to_dict
	:return: windict: <dict> key = window number: value = <charDict>
											<attack: attackvalue
											interval: intDict<timestamp: anomaly value>>
	"""
#	print "Getting attack windows"
	winDict = {}
	charDict = {} #Window characteristics: attack, interval
	intDict = {} #Interval of timestamp:score
	winCount, baseCount, atkCount = 0, 0, 0
	for key in sorted(datadict):
		attackVal = datadict[key]["attack"]
		anomalyVal = datadict[key]["anomaly_level"]
		print key, anomalyVal
		# First window is Baseline
		if attackVal == str(0) and baseCount == 0 and atkCount == 0:
			print "Baseline Window Start"
			print attackVal
			baseCount += 1
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
		# Baseline Window continues
		elif attackVal == str(0) and baseCount > 0:
			print attackVal
	#		print "Baseline Window"
			baseCount += 1
			intDict[key] = anomalyVal
		# Baseline Window ends and Attack window begins
		elif attackVal == str(1) and baseCount > 0 and atkCount == 0:
			print "Baseline Window ends"
			# Add baseline window and reset
			charDict["interval"] = intDict
			print "Window", winCount
			print charDict
			winDict[winCount] = charDict
			intDict = {}
			charDict = {}
			# Counters
			baseCount = 0
			winCount +=1
			atkCount += 1
			# Start Attack Window
#			print "Start Attack Window "
			print attackVal
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
		# First window is an Attack
		elif attackVal == str(1) and atkCount == 0 and baseCount == 0:
			print "Attack Window Start"
			print attackVal
			atkCount +=1
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
		# Attack Window continues
		elif attackVal == str(1) and atkCount > 0:
	#		print "Attack Window"
			print attackVal
			atkCount += 1
			intDict[key] = anomalyVal
		# Attack Window ends and Baseline Window begins
		if attackVal == str(0) and baseCount == 0 and atkCount > 0:
			print "Attack Window ends"

			# Add Attack Window and reset
			charDict["interval"] = intDict
			print "Window", winCount
			print charDict
			winDict[winCount] = charDict
			intDict, charDict = {}, {}
			# Counters
			atkCount, baseCount = 0, 0
			winCount += 1
			baseCount += 1
			# Start Baseline window
			print "Start Baseline Window"
			print attackVal
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
	print "Total Windows:", winCount + 1
#	print winDict
	return winDict


def get_windowed_results(windict):
	"""
	Description: Get windowed matching matrix and accuracy 
	:param windict: <dict> Dictionary returned from @get_windowed_data
	:return: results: <list> Windowed True Positive Rate,
							Windowed False Positive Rate
							Windowed True Negative Rate,
							Windowed False Negative Rate,
							Windowed Accuracy
	"""
	print("Windowed Confusion Matrix")
	TPwin, FPwin, TNwin, FNwin, = 0, 0, 0, 0
	for winNum in sorted(windict):
		window = windict[winNum]
		attack = window["attack"]
		interval = window["interval"]
		print winNum, attack, interval
		if attack == str(1):
			# True Positive
			if 'HIGH' in interval.values():
				print "TP"
				TPwin +=1
			# False Negative
			else:
				print "FN"
				FNwin +=1
		elif attack == str(0):
			# True Negative
			if 'HIGH' not in interval.values():
				print "TN"
				TNwin += 1
			# False Positive
			else:
				print "FP"
				FPwin += 1
	print TPwin, FPwin, TNwin, FNwin
	winMatrix = list(get_matching_matrix(TPwin, FPwin, TNwin, FNwin))
	winAcc = get_accuracy(TPwin, FPwin, TNwin, FNwin)
	results = winMatrix
	results.append(winAcc)
	return results


def get_per_step_results(datadict):
	"""
	Description: Get matching matrix and accuracy per step given by HTM aggregation parameter (i.e. second, minutes)
	:param datadict: <dict> Nested dictionary returned from @results_to_dict
	:return: results: <list> True Positive Rate,
	 						False Positive Rate,
							True Negative Rate,
							False Negative Rate,
							Accuracy
	"""
	print("Per Second Confusion Matrix ")
	TP, TN, FP, FN = 0, 0, 0, 0
	for key in datadict:
		anomLvl = datadict[key]["anomaly_level"]
		attackVal = datadict[key]["attack"]

		if(anomLvl == 'HIGH' and attackVal == str(1)): # Hit
			TP += 1
#			print anomLvl, attackVal,  "TP", TP
		elif(anomLvl != 'HIGH' and attackVal == str(1)): # Miss
			FN += 1
#			print anomLvl, attackVal, "FN", FN
		elif(anomLvl == 'HIGH' and attackVal == str(0)): # False Alarm
			FP += 1
#			print anomLvl, attackVal, "FP", FP
		else:#(anomLvl != 'HIGH' and attackVal == str(0)): # True Negative
			TN += 1
#			print anomLvl, attackVal, "TN", TN
	matrix = list(get_matching_matrix(TP,FP, TN, FN))
	accuracy = get_accuracy(TP, FP, TN, FN)
	results = matrix
	results.append(accuracy)
	return results


def results_to_dict(resultspath, attackpath):
	'''
	Description: Takes HTM Studio results csv file and turns it into a dictionary of dictionary
	with timestamp as key. Appends attack value to nested dictionary.
	:param resultspath: <string> Full path to HTM Studio results file (.csv)
	:param attackpath: <string> Full path to timestamped attack log file (.csv)
	:return: datadict: <dictionary>  timestamp : innerdict
	'''
	dataDict = {}
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
			dataDict[timestamp] = innerdict
	#Append Attack log to nested dictionary
	with open(attackpath, 'r') as attacklog:
		attackRows = csv.DictReader(attacklog, delimiter = ',')
		for row in attackRows:
			attackTime = row["timestamp"]
			attackValue = row["attack"]
			if attackTime in dataDict:
				dataDict[attackTime]["attack"] = attackValue
	return dataDict


if __name__ == "__main__":
	resultfiles = get_directory_files(RESULT_DIR)
	directory_exists(EVAL_DIR)
	print resultfiles
	for aFile in resultfiles:
		data = results_to_dict(aFile, ATTACK_LOG)
		split = aFile.split("/")
		fullname = split[-1]
		filename = fullname.split(".")
		print filename
		#To-do: Fix with regex
		"""
		searchpattern = "/\\w*.$"
		match = re.search(searchpattern, aFile) #fix regex to get file name only
		if match:
			print match.group()
		"""
		outFileName = EVAL_DIR + filename[0]  + "_eval.txt"
		with open(outFileName, "w+" ) as evalFile:
			evalWriter = csv.writer(evalFile)
			header = ["TPR", "FPR", "TNR", "FNR", "Acc", "TPRWin", "FPRWin", "TNRWin", "FNRWin", "AccWin"]
			evalWriter.writerow(header)
			# Get Per Second Results
			persecResults = get_per_step_results(data)
			print persecResults

			# Get Windowed Results
			windowedData = get_windowed_data(data)
			windowedResults = get_windowed_results(windowedData)

			row = persecResults + windowedResults
			evalWriter.writerow(row)