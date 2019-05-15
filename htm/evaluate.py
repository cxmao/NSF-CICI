# Author: Christina Mao
# Date Created: 04-25-2019
# Description:Takes HTM results files and evaluate results to get confusion matrix.
# Assumes rest of system background is free from attacks
# To-do: 15 minute window evaluation
# To-do: Time until anomaly detected
#---------------------------------------------------------------------------------
from __future__ import division
import os
import csv
import collections
import re

ATTACK_LOG = "/home/cmao/Repos/nsf-cici/data/experiment1/results/periodic_attack_log.csv"
RESULT_DIR = "/home/cmao/Repos/nsf-cici/data/experiment1/results/htmstudio/"
EVAL_DIR = "/home/cmao/Repos/nsf-cici/data/experiment1/eval/"

def check_directory_exists(dirpath):
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


def get_precision(TPos, FPos):
	"""
	Description: Get precision of positive predictive value (PPV)
	:param TPos: <int> Number of true positives
	:param FPos: <int> Number of false positives
	:return: precision <float>
	"""
	try:
		precision = TPos / (TPos + FPos)
		return precision
	except ZeroDivisionError:
		return 0

def get_accuracy(Tpos, Fpos, Tneg, Fneg):
	"""
	Description: Get accuracy of results
	:param Tpos: <int> Number of true positives
	:param Fpos: <int> Number of false positives
	:param Tneg: <int> number of true negatives
	:param Fneg: <int> Number of false negatives
	:return: accuracy: <float> Accuracy
	"""
	try:
		pos = Tpos + Fneg
		neg = Tneg + Fpos
		accuracy = (Tpos + Tneg) / (pos + neg)
		return accuracy
	except ZeroDivisionError:
		return 0


def validate_matrix(TPR, FPR, TNR, FNR):
	if TPR + FNR != 1:
		valid = False
	if FPR  + TNR != 1:
		valid = False
	else:
		valid = True
	return valid

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

	valid = validate_matrix(TPR, FPR, TNR, FNR)
	if not valid:
		raise Exception
		print "Results not valid"
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
	winCount, baseWin, atkWin, baseCount, atkCount, = 0, 0, 0, 0, 0
	for key in sorted(datadict):
		attackVal = datadict[key].get("attack")
		anomalyVal = datadict[key].get("anomaly_level")
#		print key, anomalyVal
		# First window is Baseline
		if attackVal == str(0) and baseCount == 0 and atkCount == 0:
#			print "Baseline Window Start"
#			print attackVal
			baseCount += 1
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
		# Baseline Window continues
		elif attackVal == str(0) and baseCount > 0:
#			print attackVal
#			print "Baseline Window"
			baseCount += 1
			intDict[key] = anomalyVal
		# Baseline Window ends and Attack window begins
		elif attackVal == str(1) and baseCount > 0 and atkCount == 0:
#			print "Baseline Window ends"
			# Add baseline window and reset counters
			charDict["interval"] = intDict
#			print "Window", winCount
#			print charDict
			winDict[winCount] = charDict
			intDict = {}
			charDict = {}
			# Counters
			baseCount = 0
			winCount +=1
			atkCount += 1
			baseWin +=1
			# Start Attack Window
#			print "Start Attack Window "
#			print attackVal
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
		# First window is an Attack
		elif attackVal == str(1) and atkCount == 0 and baseCount == 0:
#			print "Attack Window Start"
#			print attackVal
			atkCount +=1
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
		# Attack Window continues
		elif attackVal == str(1) and atkCount > 0:
	#		print "Attack Window"
#			print attackVal
			atkCount += 1
			intDict[key] = anomalyVal
		# Attack Window ends and Baseline Window begins
		if attackVal == str(0) and baseCount == 0 and atkCount > 0:
#			print "Attack Window ends"
			# Add Attack Window and reset
			charDict["interval"] = intDict
#			print "Window", winCount
#			print charDict
			winDict[winCount] = charDict
			intDict, charDict = {}, {}
			# Counters
			atkCount, baseCount = 0, 0
			winCount += 1
			baseCount += 1
			atkWin +=1
			# Start Baseline window
#			print "Start Baseline Window"
#			print attackVal
			charDict["attack"] = attackVal
			intDict[key] = anomalyVal
	print "Total Windows:", winCount
	print "Total Attack Windows:", atkWin
	print "Total Baseline Windows", baseWin
#	print winDict
	return (winCount, baseWin, atkWin, winDict)


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
		print "window", winNum, "attack", attack, interval
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
	results = [TPwin, FPwin, TNwin, FNwin]
	print results
	winMatrix = list(get_matching_matrix(TPwin, FPwin, TNwin, FNwin))
	winAcc = get_accuracy(TPwin, FPwin, TNwin, FNwin)
	winPrecision = get_precision(TPwin,FPwin)
	results.extend(winMatrix)
	results.append(winAcc)
	results.append(winPrecision)
	print results
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
	try:
		print("Per Second Matching Matrix ")
		TP, TN, FP, FN = 0, 0, 0, 0
		print len(datadict)
		for key in sorted(datadict):
			print key, datadict[key]
			anomLvl = datadict[key].get("anomaly_level")
			attackVal = datadict[key].get("attack")
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

		print TP, FP, TN, FN
		results = [TP, FP, TN, FN]
		matrix = list(get_matching_matrix(TP,FP, TN, FN))
		accuracy = get_accuracy(TP, FP, TN, FN)
		precision = get_precision(TP,FP)
		results.extend(matrix)
		results.append(accuracy)
		results.append(precision)
		print results
		return results
	except KeyError:
		KeyError



def results_to_dict(resultspath, attackpath):
	'''
	Description: Takes HTM Studio results csv file and turns it into a dictionary of dictionary
	with timestamp as key. Appends attack value to nested dictionary.
	:param resultspath: <string> Full path to HTM Studio results file (.csv)
	:param attackpath: <string> Full path to timestamped attack log file (.csv)
	:return: datadict: <dictionary>  timestamp : innerdict
	'''
	#To-Do: Add datetime format checking to check for MM/DD/YYY HH:MM:SS
	dataDict = {}
	with open(resultspath, 'r') as resultsfile, open(attackpath, 'r') as attacklog:
		resultsReader = csv.DictReader(resultsfile, delimiter = ',')
		attackReader = csv.DictReader(attacklog, delimiter=',')
		for resultRow in resultsReader:
	#		print resultRow
			timestamp = resultRow["timestamp"]
			innerdict = {}
			for ind, key in enumerate(resultRow):
				if not(key == "timestamp"):
					innerKey = key
					innerVal = resultRow[key]
					innerdict[innerKey] = innerVal
					dataDict[timestamp] = innerdict
		'''
		# Append attack log to nested dictionary
		for resultRow in resultsReader:
			timestamp = resultRow["timestamp"]
			print timestamp
		'''
		# Append attack log times
		for attackRow in attackReader:
			attackTime = attackRow["timestamp"]
			attackValue = attackRow["attack"]
			if attackTime in dataDict:
#				print timestamp, attackTime
				dataDict[attackTime]["attack"] = attackValue
#				print dataDict[attackTime]
		# Throw out rows missing attack
		rowsToDel = []
		for time in dataDict:
			if 'attack' not in dataDict[time].keys():
#				print time, dataDict[time]
				rowsToDel.append(time)
		for row in rowsToDel:
			dataDict.pop(row)
	return dataDict


if __name__ == "__main__":
	files = get_directory_files(RESULT_DIR)
	check_directory_exists(EVAL_DIR)
	for aFile in files:
		print "Evaluating " + aFile

		# To-do: Fix with regex?
		# Get Out file name
		split = aFile.split("/")
		file = split[-1]
		filename = file.split(".")

		# Get Per Step results
		outFileName = EVAL_DIR + filename[0]  + "_eval_perstep.txt"
		header = [
			"true_positive",
			"false_positive",
			"true_negative",
			"false_negative",
			"true_positive_rate",
			"false_positive_rate",
			"true_negative_rate",
			"false_negative_rate",
			"accuracy",
			"precision"]
		with open(outFileName, "w+" ) as evalFile:
			evalWriter = csv.writer(evalFile)
			evalWriter.writerow(header)

			data = results_to_dict(aFile, ATTACK_LOG)
			stepResults = get_per_step_results(data)
			evalWriter.writerow(stepResults)

		# Get Windowed results
		outFileName = EVAL_DIR + filename[0] + "_eval_window.txt"
		winHeader = ["windows",
				"base_windows",
				"attack_windows",
				"true_positive",
				"false_positive",
				"true_negative",
				"false_negative",
				"true_positive_rate",
				"false_positive_rate",
				"true_negative_rate",
				"false_negative_rate",
				"accuracy",
				"precision"]
		with open(outFileName, "w+" ) as evalFile:
			evalWriter = csv.writer(evalFile)
			evalWriter.writerow(winHeader)
			winResults = []

			winData = get_windowed_data(data)
			winDict = winData[3]
			winMatrix = get_windowed_results(winDict)
			print winData[0:3]
			winResults.extend(list(winData[0:3]))
			winResults.extend(winMatrix)
			evalWriter.writerow(winResults)