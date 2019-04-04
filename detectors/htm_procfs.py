# Author: Christina Mao 
# Date Modified: 03 March 2019
# Uses the Nupic Online Prediction Framework (OPF) API
# Modified: htm_univariate.py for /proc FS data
# Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
# Description: Creates and runs a HTM model for each field in a /proc FS processed datafile (output from format_logs.py)
# Model parameters are specified base_model_params.py. Anomaly scores are written out to csv files in "/results/<date>/""
# TO-DO: Update function documentation
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
dateMatch = re.search(r'\d{4}-\d{2}-\d{2}', _FILENAME)
_FILEDATE = str(datetime.datetime.strptime(dateMatch.group(), "%Y-%m-%d").date())
_INPUT_DIR = "/home/cmao/Repos/nsf-cici/data/clean/procfs/"
_OUTPUT_DIR =  "/home/cmao/Repos/nsf-cici/results/" + _FILEDATE + "/"

# Set Model Variables 
_ALLFIELDS = True
_ANOMALY_THRESHOLD = 0.9


def LoadData(filepath):
	if os.path.isfile(filepath):
			df = pd.read_csv(filepath)
			df_clean = df.dropna(how='any') # Drop rows with any NaN values
	return df_clean


def SetModelParams(filename, filedate, field):
	"""
	Description:
		Uses base_model_param.py to create a <field>_model_params.py file 
		with modified fieldname for the encoder. Returns a dictionary of headers and
		writes the updated file into '/config'
	Parameters:
		filename  <string> Name of file to write to for model config
		filedate <string>  Date of logdata
		field <string> Field name taken from logdata
	Returns:
		dictdump - <dict>  All headers taken from Collectl Log 
	"""
	configDir = _DIR + '/config/' + filedate + "/"
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
		modelparams <dict> - Taken from model parameters JSON
		field <string> - Fieldname to predict
	Return: 
		model <model>
	"""
	model = ModelFactory.create(modelparams) 
	# Set learning 

	# Set Inference
	model.enableInference({"predictedField": field})  # Use the field name, not encoder name
	

	return model


def GetData(df, header, field):
	"""
	Description:
	Takes dataframe and converts each row entry into a dictionary with keys:
		    * Timestamp
		    * Field 
	Parameters:
		df <pandas dataframe>
		header <list>  - header of timestamp, fieldname
	    field <int> - field specifier based off given Collectl fields
	Returns: <tuple>
	    modelInput - <list of dicts> of timestamp and selected field value
	"""
	print("Processing model input")
	modelinput = []
	for i in range(2, df.shape[0]):
		# Convert datatype
		timestamp = datetime.datetime.strptime(df.iloc[i][0], "%Y-%m-%d %H:%M:%S")
		fieldValue = float(df.iloc[i][field])
		# Format model input
		recordValue = [timestamp, fieldValue]
		record = dict(zip(header, recordValue))
		modelinput.append(record)
	return modelinput



def RunModel(model, data, filedate, field):
	"""
	Description:
	Creates HTM model based off given @params.  Writes out anomaly scores to a csv file in '/results'
	Parameters:
		data - <list of dict>
		fieldname - <string>
	Returns:
		Null
	"""
	# Check output directory exists
	if not os.path.exists(_OUTPUT_DIR):
		os.mkdir(_OUTPUT_DIR)
	os.chdir(_OUTPUT_DIR)

	resultFile = field + _CSV_NAME
	csvWriter = csv.writer(open(resultFile, "wb"))
	csvWriter.writerow(["timestamp", field, "anomaly_score"])

	#Save Model 
	print("Saving model")
	model.save( _DIR + '/model/htm_procfs/' + str(date.today()))

	# Offline Results
	print("Running model")
	results = []
	for i in range(0, len(data)):
		result = model.run(data[i])
		# Log results
		results.append(result)
		anomalyScore = results[i].inferences['anomalyScore']
		csvWriter.writerow([data[i]['timestamp'], data[i][field], anomalyScore]) 
	print("Results written to " + _OUTPUT_DIR + resultFile)

	# Online Results
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
			configFilename = str(date.today()) + "_" + fields[i] + '.py'
			modelParams = SetModelParams(configFilename, _FILEDATE, fields[i])
			model = CreateModel(modelParams, fields[i])
			# If results already exist, then skip
			if (not os.path.isfile(_OUTPUT_DIR + fields[i] + _CSV_NAME)):
				header = [fields[0], fields[i]]
				modelInput = GetData(df, header, fields[i])
				RunModel(model, modelInput, _FILEDATE, fields[i])
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
	