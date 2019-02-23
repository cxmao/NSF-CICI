# Author: Christina Mao 
# Date: 14 February 2019
# Uses the Nupic Online Prediction Framework (OPF) API
# Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
# Description: 
# 
# To-do: Fix hard-coded file paths
# To-do: Multiple files - continuous stream  
# To-do: Multiencoder for all fields 
# To-do: Add function documentation
#-------------------------------------------------------------------------------------------------------
import os
import csv
import datetime
import logging
# File Processing
import simplejson as json
from string import Template
# Plotting 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly as py
import plotly.figure_factory as ff

# Nupic OPF
import base_model_params as mp
from nupic.frameworks.opf.model_factory import ModelFactory

#--------------------------------------------------------------------------------------------------------
# System variables
_LOGGER = logging.getLogger(__name__)
_OUTPUT_PATH = "anomaly_scores.csv"


# Data File Paths 
_DIR = os.getcwd()
_BASE_MODEL_PARAMS_PATH = _DIR + "/base_model_params.py"
_CPU_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190215.cpu"
_DISK_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.dsk"



# Model variables 
# Select based on Collectl log headers
#_FIELD_SELECTOR = [13, 25, 37, 49, 61, 73, 85, 97] #CPU Interrupts
_FIELD_SELECTOR = [5,9] #Disk Read/Writes

#---------------------------------------------------------------------------------------------------------

def GetFieldName(header,index):
	"""
	Description:
		Retrieve the log field name 

	Parameters: 
		index - <int> index of _FIELD_SELECTOR

	Returns: 
		aField - <string> Corresponding field name in the given Collectl Log 
	"""
	aField = header[index]
	return	aField

def SetModelParams(filename,field):
	"""
	Description: 
		Updates the xxx_model_params.py JSON file. Sets the encoder fields with appropriate fieldname. Returns a dictionary taken 
		the modified parameter. 
	Parameters: 
		filename - <string> Name of file to write to
		field - <string> Field name taken from Collectl Log 
	Returns:
		dictdump - <dict> 

	"""
#	copyfile(_BASE_MODEL_PARAMS_PATH, filename)

	if not (os.path.exists( _DIR + '/config')):
		os.mkdir( _DIR +'/config')

	#Create a new Python file 
	with open(_DIR + '/config/' + filename, "w+") as f: 
		data = json.dumps(mp.MODEL_PARAMS, sort_keys=False, indent=4) #Convert python object to a serialized JSON string 
		#Modify parameters in the new file
		temp_data = Template(data)
		final = temp_data.substitute(fieldname=field)
		# Write as a dictionary to load into CreateModel()
		dictdump = json.loads(final)
		# Write JSON data as a Python Object to file 
		f.write("MODEL_PARAMS = ")
		f.write(final)
	#Save and close file 
	os.chdir(_DIR)
	f.close()
	return dictdump

def GetData(datapath, field):
	"""
	Description:
	    Takes default Collectl Plot files and converts each row entry  into a dictionary with keys: 
	    * Timestamp
	    * Field 

    Parameters:
	    datapath - <string> File path to Collectl Plot formatted files
	    field  - <int> field specifier based off given Collectl fields
    
    Returns: <tuple>
		headers - <list> of all field headers
	    modelInput - <list of dicts> of timestamp and selected field value
	"""
	with open(datapath) as openfile:
		reader = csv.reader(openfile)
		header = []
		modelInputHdr = []
		modelInput = []
		for row in reader:
			record_value = []
#			row = reader.next()
			# Get Header
			if ( row[0] == '#Date' and not header ):
				# Get selected field header
				modelInputHdr.append('timestamp')
				modelInputHdr.append(row[field]) 
				#Get all field headers of the log besides date and time
				header = row

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

				record = dict(zip(modelInputHdr,record_value))
				modelInput.append(record)
	return header,modelInput


def CreateModel(params):
	"""
	Parameters: 
		params - <dict> from model parameters JSON
	"""
	return ModelFactory.create(params)

	"""
	# With a YAML config file 
		with open(_MODEL_PARAMS_PATH, "r") as f:
			modelParams = yaml.safe_load(f)
		return ModelFactory.create(modelParams)
	"""

def RunModel(params, data, field):
	"""
	Description: 
	Creates HTM model based off given @params.  Writes out anomaly scores to a csv file.
	Parameters: 
		data - <list of dict> 
		fieldname - <string>

	Returns: 
		None
	"""
	model = CreateModel(params)
	model.enableInference({"predictedField": field}) #Use the field name, not the encoder name
	
	if not os.path.exists( _DIR + '/results' ):
		os.mkdir( _DIR + '/results' )
	os.chdir(_DIR + '/results')
	csvWriter = csv.writer(open( field + "_anomaly_scores.csv","wb"))
	csvWriter.writerow(["timestamp", field, "anomaly_score"])

	# Offline Results
	results = []
	for i in range(len(data[1])):
		results.append(model.run(data[1][i]))
		# Append Anomaly Score and write out results to CSV file 
		anomalyScore = results[i].inferences['anomalyScore']
		csvWriter.writerow([data[1][i]['timestamp'], data[1][i][field],anomalyScore]) 
	print ("Results written to " + _DIR + "/results/" + field + "_anomaly_scores.csv")
	"""
	# Logger
	 	if anomalyScore > _ANOMALY_THRESHOLD:
	      _LOGGER.info("Anomaly detected at [%s]. Anomaly score: %f.",
	                    result.rawInput["timestamp"], anomalyScore)
	"""
	return 0

	# Online Results



def main():
	for i in range(len(_FIELD_SELECTOR)):
		modelInput = GetData(_DISK_DATA_PATH, _FIELD_SELECTOR[i])
		fieldName = GetFieldName(modelInput[0],_FIELD_SELECTOR[i])
		modelParams = SetModelParams(fieldName + ".py", fieldName)
		RunModel(modelParams,modelInput, fieldName)

if __name__ == "__main__":
	main ()

	