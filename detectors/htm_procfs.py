""" 
Author: Christina Mao 
Date Created: 03 March 2019
Uses the Nupic Online Prediction Framework (OPF) API
Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
Description: Creates and runs a HTM model for each field in a /proc FS processed datafile (output from format_logs.py)
Model parameters are specified base_model_params.py. Anomaly scores are written out to csv files in "/results/<date>/""

"""
#-------------------------------------------------------------------------------------------------------
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


# System Variables
_LOGGER = logging.getLogger(__name__)
_DIR = os.getcwd()
_BASE_MODEL_PARAMS_PATH = _DIR + "/base_model_params.py"
_CSV_NAME = "_anomaly_scores.csv"

# Set Data Paths
_INPUT_DIR = "/home/cmao/Repos/nsf-cici/data/procfs/"
_OUTPUT_DIR= _DIR + '/results/' + filter(str.isdigit, _DATA_PATH) + '/'

# Set Model Variables 
_ALLFIELDS = True
# Select based on Collectl log headers
#_FIELD_SELECTOR = [13, 25, 37, 49, 61, 73, 85, 97] #CPU Interrupts
_FIELD_SELECTOR = [5, 9] #Disk Read/Writes

_ANOMALY_THRESHOLD = 0.80

#---------------------------------------------------------------------------------------------------------


def GetHeader(filepath):
	"""
	Description:
		Get header fields from csv file path
	Parameters:
		datapath - <string>  full file path 
	Returns:
		header - <list> 
	"""
	header = []
	with open(filepath) as f: 
		reader = csv.reader(f)
		for row in  reader:
			if (row[0] == '#Date' and not header):
				header = row
	return header


def GetFieldName(header,index):
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


def SetModelParams(filename,field):
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
	if not (os.path.exists(_DIR + '/config')):
		os.mkdir(_DIR + '/config')
	#Create a new configuration Python file 
	with open(_DIR + '/config/' + filename, "w+") as f:
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


def GetData(logs, field):
	"""
	Description:
	    Formats @collectl into NuPIC data file. Takes default Collectl Plot files and converts each row entry 
	    into a dictionary with keys:
	    * Timestamp
	    * Field 
	Parameters:
	    datapath - <string> File path to Collectl Plot formatted files
	    field  - <int> field specifier based off given Collectl fields
	Returns: <tuple>
		headers - <list> of all field headers
	    modelInput - <list of dicts> of timestamp and selected field value
	"""
	with open(logs) as openfile:
		reader = csv.reader(openfile)
		header = []
		modelInputHdr = []
		modelInput = []
		for row in reader:
			record_value = []
#			row = reader.next()
			# Get Header
			if (row[0] == '#Date' and not header):
				# Get selected field header
				modelInputHdr.append('timestamp')
				modelInputHdr.append(row[field])
				#Get all field headers of the log besides date and time
				header = row

			# Format into a record dictionary
			elif (row[0].isdigit()): 
				# Format date string to a datetime format
				date_string = row[0][0:4] + "-" + row[0][4:6] + "-" + row[0][6:8] + " " + row[1]
				# Cast to a datetime object
				timestamp_value = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
				if(str.isdigit(row[field]) or float(row[field])):
					# Cast to float type
					field_value = float(row[field])
					# Write to record dictionary
					record_value.append(timestamp_value)
					record_value.append(field_value)
					record = dict(zip(modelInputHdr, record_value))
					modelInput.append(record)
	return header, modelInput


def CreateModel(params):
	"""
	Description: 
	Parameters: 
		params - <dict> taken from model parameters JSON
	Return: 
		Model instance
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
	Creates HTM model based off given @params.  Writes out anomaly scores to a csv file in '/results'
	Parameters:
		data - <list of dict>
		fieldname - <string>
	Returns:
		Null
	"""
	model = CreateModel(params)
	model.enableInference({"predictedField": field})#Use the field name, not the encoder name
	
	# Check output directory exists
	if not os.path.exists(_OUTPUT_DIR):
		os.mkdir(_OUTPUT_DIR)
	os.chdir(_OUTPUT_DIR)

	csvWriter = csv.writer(open(field + _CSV_NAME, "wb"))
	csvWriter.writerow(["timestamp", field, "anomaly_score"])

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
	'''
	# Write to Logger 
	if anomalyScore > _ANOMALY_THRESHOLD:
		_LOGGER.basicConfig(filename='anomaly.log', level=logging.INFO)
		_LOGGER.info("Anomaly detected at [%s]. Anomaly score: %f.",
                    result.rawInput["timestamp"], anomalyScore)
	'''
	return 0

	
if __name__ == "__main__":
	if(not _ALLFIELDS):
		for i in range(len(_FIELD_SELECTOR)):
			modelInput = GetData(_INPUT_DIR, _FIELD_SELECTOR[i])
			fieldName = GetFieldName(modelInput[0],_FIELD_SELECTOR[i])
			modelParams = SetModelParams(fieldName + ".py", fieldName)
			RunModel(modelParams, modelInput, fieldName)
	else: # Select Fields 
		header = GetHeader(_INPUT_DIR)
		print header
		for i in range(2, len(header)):
			# Check if results exist, then skip
			if (not os.path.isfile(_OUTPUT_DIR + header[i] + _CSV_NAME)):
				modelInput = GetData(_INPUT_DIR, i)
				if (modelInput[1] != []):#Input data is not empty
					fieldName = GetFieldName(modelInput[0], i)
					print fieldName
					modelParams = SetModelParams(fieldName + ".py", fieldName)
					print ("Running Model for " + header[i])
					RunModel(modelParams, modelInput, fieldName)