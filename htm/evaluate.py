# Author: Christina Mao
# Date Created: 04-25-2019
# Description:Takes HTM results files and evaluate results to get confusion matrix.
# Assumes rest of system background is free from attacks
#
#---------------------------------------------------------------------------------

import os
import csv


RESULTDIR = "/home/cmao/Repos/nsf-cici/data/experiment1/results/"


def validatepath():
	try:
		resultfiles = []
		if os.path.isdir(RESULTDIR):
			for r, d, f in os.walk(RESULTDIR):
				for file in f:
					resultfiles.append(os.path.join(r,file))
	except:
		print(RESULTDIR + " is not a directory")
	return resultfiles
# Get True Positive Rate (TPR) Sensitivity
def GetTPR():
	return

# Get True Negative Rate (TNR) Specificity
def GetTNR():
	return

# Get False Positive Rate (FPR) Fall-out
def GetFPR():
	return
# Get False Negative Rate (FNR) Miss-rate
def GetFNR():
	return
def main():
	# Gene
	# Check that file exists
	results = validatepath()
	for f in results:
		file  = open(f, "r")
		csvreader = csv.reader(file)




	return
if __name__ == "__main__":
	main()