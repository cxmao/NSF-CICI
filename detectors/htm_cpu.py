# Author: Christina Mao 
# Date: 14 February 2019
# Uses the Nupic Online Prediction Framework (OPF) API
# Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
# Description: 
# 
#
import os
import csv
import datetime
import cpu_model_params
import yaml
from nupic.frameworks.opf.model_factory import ModelFactory

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_MODEL_PARAMS_PATH = os.path.join(_CURRENT_DIR, "cpu_model_params.yaml")

_OUTPUT_PATH = "anomaly_scores.csv"

print(_MODEL_PARAMS_PATH)


#--------------------------------------------------------------------------------
# Data File Paths 
_CPU_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.cpu"
_DISK_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.dsk"
_FiELD_SELECTOR = 10

# To-do: Unzip file
# To-do: Encode CPU File into one value


def Get_CPU_data(datasetpath, field):
	"""
    @params datasetpath - string, File path to Collectl Plot formatted files
    @params field  - int, field specifier
    Output: 
	"""
	#To-do:Check field argument 

	with open(datasetpath) as openfile:
		reader = csv.reader(openfile)
		headers = []
		modelInput = []
		for x in range(50):
			record_value= []
			row = reader.next()
			# Get Header
			if ( row[0] == '#Date' and not headers ):
				headers.append('timestamp')
				headers.append(row[field]) #Remove this line if using all fields
#				for field in row[2:-1]: #Gets all fields of the log
#					headers.append(field)
			# Format into a record dictionary
			elif ( row[0].isdigit() ): 
				# Format date string to a datetime format
				date_string= row[0][0:4] + "-" + row[0][4:6] + "-" + row[0][6:8] + " " + row[1]
				# Cast to a datetime object 
				timestamp_value = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
				# Cast to float type 
				field_value = float(row[field])

				record_value.append(timestamp_value)
				record_value.append(field_value)

				record = dict(zip(headers,record_value))
				modelInput.append(record)
#	print modelInput[0:-1]
	return modelInput


def CreateModel():
	return ModelFactory.create(cpu_model_params.MODEL_PARAMS)

	# With a YAML config file 
#	with open(_MODEL_PARAMS_PATH, "r") as f:
#		modelParams = yaml.safe_load(f)
#	return ModelFactory.create(modelParams)


def RunModel():
	model = CreateModel()
	model.enableInference({"predictedField": '[CPU:0]Totl%'}) #Use the field name, not the encoder name
	csvWriter = csv.writer(open(_OUTPUT_PATH,"wb"))
	csvWriter.writerow(["timestamp", "total_utilization%", "anomaly_score"])

	# Offline Results
	results = []
	modelInput = Get_CPU_data(_CPU_DATA_PATH, _FiELD_SELECTOR)
	for i in range(len(modelInput)):
		results.append(model.run(modelInput[i]))

		# Write to CSV file 
		anomalyScore = results[i].inferences['anomalyScore']
		csvWriter.writerow([modelInput[i]['timestamp'], modelInput[i]['[CPU:0]Totl%'],anomalyScore]) 

	return 0 

	# Online Results


if __name__ == "__main__":
	data = Get_CPU_data(_CPU_DATA_PATH, _FiELD_SELECTOR)
	RunModel()
