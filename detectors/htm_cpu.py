# Author: Christina Mao 
# Date: 14 February 2019
# Uses the Nupic Online Prediction Framework (OPF) API
# Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
# Description: 
# 
#
import os
import csv
import yaml
from nupic.frameworks.opf.model_factory import ModelFactory

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_MODEL_PARAMS_PATH = os.path.join(_CURRENT_DIR, "model_params.yaml")

_OUTPUT_PATH = "anomaly_scores.csv"

print(_MODEL_PARAMS_PATH)


#--------------------------------------------------------------------------------
# Data File Paths 
_CPU_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.cpu"
_DISK_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.dsk"
_FiELD_SELECTOR = 10

# To-do: Unzip file
# To-do: Encode CPU File into one value

#--------------------------------------------------------------------------------
# @params datasetpath- File path to Collectl Plot formatted files
# @params field  - int, field specifier
#
#--------------------------------------------------------------------------------
def Get_CPU_data(datasetpath, field):
	# Check field argument 
	print field
	with open(datasetpath) as openfile:
		reader = csv.reader(openfile)
		headers = []
		for x in range(50):
			record = []
			row = reader.next()
			# Get Header
			if ( row[0] == '#Date' and not headers ):
				headers.append('Timestamp')
				headers.append(row[field]) #Remove this line if using all fields
#				for field in row[2:-1]: #Gets all fields
#					headers.append(field)
			# Format into a record dictionary
			elif (row[0].isdigit()):
				record.append(row[0] + " " + row[1])
				record.append(float(row[field]))
				modelInput = dict(zip(headers,record))
		print modelInput
		return modelInput


def CreateModel():
	with open(_MODEL_PARAMS_PATH, "r") as f:
		modelParams = yaml.safe_load(f)
		return ModelFactory.create(modelParams)


def RunModel(data):
	model = CreateModel()
	model.enableInference({"predictedField": 'total_utilization'})
	csvWriter = csv.writer(open(_OUTPUT_PATH,"wb"))
	csvWriter.writerow(["timestamp", "total_utilization%", "anomaly_score"])

	# Offline Results
	results = []
#	results.append(model.run(modelInput))

	# Online Results


if __name__ == "__main__":
	data = Get_CPU_data(_CPU_DATA_PATH, _FiELD_SELECTOR)
	RunModel(data)
