# Author: Christina Mao 
# Date Created: 04 March 2019
# Uses the Nupic Online Prediction Framework (OPF) API
# Modified: htm_univariate.py for /proc FS data
# Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
# Description: Creates and runs a HTM model for each field in a /proc FS processed datafile (output from format_logs.py)
# Base model parameters are specified by base_model_params.py. 
# Anomaly scores are written out as csv files to directory specified by _OUTPUT_DIR 
# TO-DO: Update function documentation
# To-Do: Pull Aggregate logs function from htm_streaming
# To-Do: Python script to aggregate logs
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
import base_model_params as modelparams
from nupic.frameworks.opf.model_factory import ModelFactory
# Data Processing
import pandas as pd
import re


# System Variables
_LOGGER = logging.getLogger(__name__)
_DIR = os.getcwd()
_OUTFILE_SUF = "_anomaly_scores.csv"

# Set Input Data Paths
_FILENAME = "2019-04-02_context_clean.csv"
dateMatch = re.search(r'\d{4}-\d{2}-\d{2}', _FILENAME)
dateStrip = str(datetime.datetime.strptime(dateMatch.group(), "%Y-%m-%d").date())
_FILEDATE = filter(str.isdigit,dateStrip) # 
_INPUT_DIR = "/home/cmao/Repos/nsf-cici/data/test/clean/" 

# Set Output Data Paths

_OUTPUT_DIR = "/home/cmao/Repos/nsf-cici/htm/results/test/" + _FILEDATE  + "/"

# Set Model Parameters
_ALLFIELDS = True # Run model for all columns in input file
#To-do: Write code for select fields
_FIELD_SELECTOR = [1] 
_LEARN = True# Set CLA classifier
_ANOMALY_THRESHOLD = 0.80 # Default threshold is 0.80


def LoadData(filepath):
	try:
		assert(os.path.isfile(filepath))
	except:
		print(filepath + " does not exist")
	else:
		df = pd.read_csv(filepath)
		df_clean = df.dropna(how='any')# Drop rows with any NaN values
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
		data = json.dumps(modelparams.MODEL_PARAMS, sort_keys=False, indent=4)#Convert python object to a serialized JSON string 
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
	print("Creating Model")
	model = ModelFactory.create(modelparams) 
	# Set field to predict
	model.enableInference({"predictedField": field})  # Use the field name, not encoder name
	# Set learning 
	if _LEARN: 
		model.enableLearning()
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
	print("Processing Model Input")
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

def PrintModelParams(model):
	print("Model Parameters:")
	print("Inference:", model.isInferenceEnabled())
	print("Learning:", model.isLearningEnabled())

def SaveModel(model):
	print("Saving Model")
	#model.FinishLearning()
	model.save( _DIR + '/model/htm_procfs/' + _FILEDATE)


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
	# Check output directory path
	print("Checking Output Directory")
	# To-Do: Sanitize filename
	#safeOutDir = _OUTPUT_DIR.text.replace('/', '_')
	if(not os.path.exists(_OUTPUT_DIR)):
		os.makedirs(_OUTPUT_DIR)
	os.chdir(_OUTPUT_DIR)

	# Offline Results
	print("Running Model")
	resultFile = field + _OUTFILE_SUF
	csvWriter = csv.writer(open(resultFile, "wb"))
	csvWriter.writerow(["timestamp", field, "anomaly_score"])
	results = []
	print len(data)
	for i in range(0, len(data)):
		print("Runtime Stats:",  model.getRuntimeStats())
		result = model.run(data[i])
		# Log results
		results.append(result)
		# Append Anomaly Score and write out results to CSV file
		anomalyScore = results[i].inferences['anomalyScore']
		csvWriter.writerow([data[i]['timestamp'], data[i][field], anomalyScore]) 
	print("Results written to " + _OUTPUT_DIR + resultFile)

	#Save model 
	SaveModel(model)
	
	# Online Results
	if anomalyScore > _ANOMALY_THRESHOLD:
		_LOGGER.info("Anomaly detected at [%s]. Anomaly score: %f.",
                    result.rawInput["timestamp"], anomalyScore)
	return

def main():
	# Load data into Pandas dataframe
	df = LoadData(_INPUT_DIR + _FILENAME)
	fields = list(df.columns.values)
	# Run model for all fields in datafile
	if(_ALLFIELDS):
		# Run HTM model for each metric
		for i in range(1, len(fields)):
			configFilename = str(date.today()) + '_' + fields[i] + '.py'
			timestamp = fields[0]
			metric = fields[i]
			# Create new model
			modelParams = SetModelParams(configFilename, _FILEDATE, metric)
			model = CreateModel(modelParams, metric)
			PrintModelParams(model)
			# Skip if results already exist
			if (not os.path.isfile(_OUTPUT_DIR + fields[i] + _OUTFILE_SUF)):
				header = [timestamp, metric]
				modelInput = GetData(df, header, metric)
				RunModel(model, modelInput, _FILEDATE, metric)
	"""
	#To-do: Finish and Test
	else: #Run for select fields in datafile 
		# Run HTM model for selected metrics
		for i in range(1, len(_FIELD_SELECTOR)):
			configFilename = str(date.today()) + '_' + fields[i] + '.py'
			timestamp = fields[0]
			metric =  fields[i]
			# Create new model 
			modelParams = SetModelParams(configFilename, _FILEDATE, metric)
			model = CreateModel(modelParams, metric)
			PrintModelParams(model)
			# Skip if results already exist
			if (not os.path.isfile(_OUTPUT_DIR + fields[i] + _CSV_NAME)):
				header = [timestamp, metric]
				modelInput = GetData(df, header, metric)
				RunModel(model, modelInput, _FILEDATE, metric)
	"""
	return


if __name__ == '__main__':
	logging.basicConfig(level=logging.INFO)
	main()