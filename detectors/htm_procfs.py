# Author: Christina Mao 
# Date Modified: 03 March 2019
# Uses the Nupic Online Prediction Framework (OPF) API
# Modified: htm_univariate.py for /proc FS data
# Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
# Description: Creates and runs a HTM model for each field in a /proc FS processed datafile (output from format_logs.py)
# Model parameters are specified base_model_params.py. Anomaly scores are written out to csv files in "/results/<date>/""
#-------------------------------------------------------------------------------------------------------
from datetime import datetime
from datetime import date
import os
import csv
import datetime
import logging
# File Processing
import simplejson as json
from string import Template
# Nupic OPF
import base_model_params as mp
from nupic.frameworks.opf.model_factory import ModelFactory
# Data Processing
import pandas as pd
import re


# System Variables
_LOGGER = logging.getLogger(__name__)
_DIR = os.getcwd()
_BASE_MODEL_PARAMS_PATH = _DIR + "/base_model_params.py"
_CSV_NAME = "_anomaly_scores.csv"

# Set Data Paths
_FILENAME = "2019-04-02_context_nupic.csv"
_INPUT_DIR = "/home/cmao/Repos/nsf-cici/data/clean/procfs/"
_OUTPUT_DIR =  "/home/cmao/Repos/nsf-cici/results/" + filter(str.isdigit, _INPUT_DIR) + "/"

# Set Model Variables 
_ALLFIELDS = True
# Select based on Collectl log headers
#_FIELD_SELECTOR = [13, 25, 37, 49, 61, 73, 85, 97] #CPU Interrupts
#_FIELD_SELECTOR = [5, 9] #Disk Read/Writes

_ANOMALY_THRESHOLD = 0.9


def LoadData(filepath):
	if os.path.isfile(filepath):
			df = pd.read_csv(filepath)
			df_clean = df.dropna(how='all')
	return df_clean

'''
def GetFields(filepath):
	"""
	Description:
		Get header fields from csv file path
	Parameters:
		datapath - <string>  full file path 
	Returns:
		header - <list> 
	"""
	fields = []
	with open(filepath) as f: 
		reader = csv.reader(f)
		fields =  reader.next()
	return fields
 

def GetFieldName(header, index):
	"""
	Description:
		Get the log field name
	Parameters:
		index - <int> index of _FIELD_SELECTOR
	Returns:
		aField - <string> Corresponding field name in the given Collectl Log
	"""
	aField = header[index]
	return aField
'''

def SetModelParams(filename, field):
	"""
	Description:
		Uses base_model_param.py to create a <field>_model_params.py file 
		with modified fieldname for the encoder. Returns a dictionary of headers and
		writes the updated file into '/config'
	Parameters:
		filename - <string> Name of file to write to
		field - <string> Field name taken from Collectl Log
	Returns:
		dictdump - <dict>  All headers taken from Collectl Log 
	"""
	configDir = _DIR + '/config/' + str(date.today())
	if not (os.path.exists(configDir)):
		os.mkdir(configDir)
	#Create a new configuration Python file 
	with open(configDir + filename, "w+") as f:
		data = json.dumps(mp.MODEL_PARAMS, sort_keys=False, indent=4)#Convert python object to a serialized JSON string 
		# Modify parameters in the new file
		temp_data = Template(data)
		final = temp_data.substitute(fieldname=field)
		# Write as a dictionary to load into CreateModel()
		dictdump = json.loads(final)
		# Write JSON data as a Python Object to file
		f.write("MODEL_PARAMS = ")
		f.write(final)
	# Save and close file
	os.chdir(_DIR)
	f.close()
	return dictdump


def CreateModel(modelparams, field):
	"""
	Description: Instantiate model object
	Parameters: 
		modelparams - <dict> taken from model parameters JSON
		field <string> - fieldname to predict
	Return: 
		Model instance
	"""
	model = ModelFactory.create(modelparams)
	model.enableInference({"predictedField": field})
	return model


def GetData(df, header, field):
	"""
	Description:
	    Formats @collectl into NuPIC data file. Takes default Collectl Plot files 
	    and converts each row entry into a dictionary with keys:
		    * Timestamp
		    * Field 
	Parameters:
		df <pandas dataframe>
		header <list>  - header of timestamp, fieldname
	    field <int> - field specifier based off given Collectl fields
	Returns: <tuple>
	    modelInput - <list of dicts> of timestamp and selected field value
	"""

	modelinput = []
	for i in range(2, df.shape[0]):
		# Convert datatype
		timestamp = datetime.datetime.strptime(df.iloc[i][0], "%Y-%m-%d %H:%M:%S")
		fieldValue = float(df.iloc[i][field])
		# Format model input
		recordValue = [timestamp, fieldValue]
		record = dict(zip(header, recordValue))
		print record
		modelinput.append(record)
	return modelinput



def RunModel(model, data, field):
	"""
	Description:
	Creates HTM model based off given @params.  Writes out anomaly scores to a csv file in '/results'
	Parameters:
		data - <list of dict>
		fieldname - <string>
	Returns:
		Null
	"""
	#model = CreateModel(modelparams)
	#model.enableInference({"predictedField": field})#Use the field name, not the encoder name
	
	# Check output directory exists
	if not os.path.exists(_OUTPUT_DIR):
		os.mkdir(_OUTPUT_DIR)
	os.chdir(_OUTPUT_DIR)

	csvWriter = csv.writer(open(field + _CSV_NAME, "wb"))
	csvWriter.writerow(["timestamp", field, "anomaly_score"])

	#Save Model 
	print("Saving model")
	model.save( _DIR + '/model/htm_procfs/' + str(date.today()))
	print("Running model")
	# Offline Results
	results = []
	for i in range(len(data[1])):
		result = model.run(data[1][i])
		# Log results
		results.append(result)
		# Append Anomaly Score and write out results to CSV file
		anomalyScore = results[i].inferences['anomalyScore']
		csvWriter.writerow([data[1][i]['timestamp'], data[1][i][field], anomalyScore]) 
	print("Results written to " + _OUTPUT_DIR + field + _CSV_NAME)

	# Online Results
	# Write to Logger 
	if anomalyScore > _ANOMALY_THRESHOLD:
		_LOGGER.info("Anomaly detected at [%s]. Anomaly score: %f.",
                    result.rawInput["timestamp"], anomalyScore)
	return

def main():
	
	if(_ALLFIELDS):
		# Load data into Pandas dataframe
		df = LoadData(_INPUT_DIR + _FILENAME)
		fields = list(df.columns.values)

		# Run HTM model for each field
		for i in range(1, len(fields)):
			modelParams = SetModelParams(fields[i] + '.py', fields[i])
			model = CreateModel(modelParams, fields[i])
			# If results already exist, then skip
			#if (not os.path.isfile(_OUTPUT_DIR + fields[i] + _CSV_NAME)):
			# Get header
			header = [fields[0], fields[i]]
			# Get model input
			modelInput = GetData(df, header, fields[i])
			#print modelInput
			#RunModel(model, modelInput, fields[i])
			"""
				for index, row in df.iterrows():
					if(index > 2):
						# Convert datatype
						timestamp = datetime.datetime.strptime(row[fields[0]], "%Y-%m-%d %H:%M:%S")
						fieldValue = float(row[fields[i]])
						# Format model input
						recordValue = [timestamp, fieldValue]
						record = dict(zip(header, recordValue))
						print ("Model Input")
						print record
						# Run model on input
					#	result = model.run(modelinput)
						#print result
				

				
				if (modelInput[1] != []):#Input data is not empty
					fieldName = GetFieldName(modelInput[0], i)
					print fieldName
					modelParams = SetModelParams(fieldName + ".py", fieldName)
					print ("Running Model for " + header[i])
					RunModel(modelParams, modelInput, fieldName)
				"""
		return


if __name__ == "__main__":
	logging.basicConfig(level=logging.INFO)
	main()

	
	"""
	else: # Select Fields 
		for i in range(len(_FIELD_SELECTOR)):
			modelInput = GetData(_INPUT_DIR, _FIELD_SELECTOR[i])
			fieldName = GetFieldName(modelInput[0],_FIELD_SELECTOR[i])
			modelParams = SetModelParams(fieldName + ".py", fieldName)
			RunModel(modelParams, modelInput, fieldName)
	"""
	