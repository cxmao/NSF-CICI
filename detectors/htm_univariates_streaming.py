""" 
Author: Christina Mao 
Date Created: 14 February 2019
Uses the Nupic Online Prediction Framework (OPF) API
Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
Description: Creates and runs a HTM model for each field for a given Collectl Plot  file.
Model parameters are given by base_model_params.py. Anomaly scores are written out to csv files in '/results'

To-do: Fix hard-coded file paths
To-do: Multiple files - continuous stream  
To-do: Multiencoder for all fields 
To-do: Add function documentation
"""
#-------------------------------------------------------------------------------------------------------
import os
import csv
import datetime
import logging
# File Processing
import simplejson as json
from string import Template
import glob
import gzip
# Nupic OPF
import base_model_params as mp
from nupic.frameworks.opf.model_factory import ModelFactory

#--------------------------------------------------------------------------------------------------------
# System variables
_LOGGER = logging.getLogger(__name__)
_DIR = os.getcwd()
_BASE_MODEL_PARAMS_PATH = _DIR + "/base_model_params.py"
_CSV_NAME = "_anomaly_scores.csv"

# Data Paths
_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/collectl_streaming" #Absolute path to Collectl  logs directory
_LOG_TYPE = ["cpu", "dsk", "net", "numa", "prc", "tab"]
_OUTPUT_PATH = _DIR + '/results/' + filter(str.isdigit, _DATA_PATH) + '/'

# Model variables 
_ALL = False #All fields in the log
# Select based on Collectl log headers
_FIELD_SELECTOR = [13]
#_FIELD_SELECTOR = [13, 25, 37, 49, 61, 73, 85, 97] #CPU Interrupts
#_FIELD_SELECTOR = [5, 9] #Disk Read/Write
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


def AggregateLogs(dirpath, logtype):
	"""
	Description: Appends and formats Collectl logs (compressed .gzip files) over multiple days into one file
	Parameters: 
		logtype - file extension of the log to aggregate into one (i.e. cpu, dsk, net)
	Returns:
		Path to 
	""" 
	#Check directory path exists and is a directory
	if not (os.path.exists(dirpath) and os.path.isdir(dirpath)):
		try: 
			raise ValueError
		except ValueError:
			print ("The directory" + _DATA_PATH + "does not exist or is not a directory. Exiting...")
	#filelist = []
	agglog = open('logtype_aggregate.log', 'wb')
		#Search list of files for logs of specified log type 
	for filename in sorted(os.listdir(dirpath)):
		if filename.endswith(logtype +'.gz'):
			#Check that dates align 
			#print(int(filter(str.isdigit,filename)))
			#Read from GZIP files and append
			fullpath = os.path.join(dirpath,filename)
			with gzip.open(fullpath, 'rb') as f:
				for line in f:
					agglog.write(line)
					#agglog.writerow(line)
	print "Finished aggregating logs"
	return 
	#print filelist
			


def GetData(filepath, field):
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
	print "Formatting data"
	with open(filepath) as openfile:
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
	print "Building model"
	#Construct the Base Model
	model = CreateModel(params)
	model.enableInference({"predictedField": field})#Use the field name, not the encoder name
	#model.enableLearning()
	
	#Check directory for output (anomaly scores) exists
	if not os.path.exists(_OUTPUT_PATH):
		os.mkdir(_OUTPUT_PATH)
	os.chdir(_OUTPUT_PATH)

	#Create anomaly scores file 
	csvWriter = csv.writer(open(field + _CSV_NAME, "wb"))
	csvWriter.writerow(["timestamp", field, "anomaly_score"])

	#Save Model 
	print "Saving model"
	model.save( _DIR + '/model/')

	print "Running model"
	# Offline Results
	results = []
	for i in range(len(data[1])):
		result = model.run(data[1][i])
		# Log results
		results.append(result)
		# Append Anomaly Score and write out results to CSV file
		anomalyScore = results[i].inferences['anomalyScore']
		csvWriter.writerow([data[1][i]['timestamp'], data[1][i][field], anomalyScore]) 
	print("Results written to " + _OUTPUT_PATH + field + _CSV_NAME)

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
	if(not _ALL):
		for i in range(len(_FIELD_SELECTOR)):
			data = AggregateLogs(_DATA_PATH, _LOG_TYPE[0])
			modelInput = GetData("logtype_aggregate.log", _FIELD_SELECTOR[i])
			fieldName = GetFieldName(modelInput[0],_FIELD_SELECTOR[i])
			modelParams = SetModelParams(fieldName + ".py", fieldName)
			RunModel(modelParams, modelInput, fieldName)
	else:
		header = GetHeader(_DATA_PATH)
		print header 
		for i in range(2, len(header)):
			# Check if results exist, then skip
			if (not os.path.isfile(_OUTPUT_PATH + header[i] + _CSV_NAME)):
				modelInput = GetData(_DATA_PATH, i)
				if (modelInput[1] != []):#Input data is not empty
					fieldName = GetFieldName(modelInput[0], i)
					print fieldName
					modelParams = SetModelParams(fieldName + ".py", fieldName)
					print ("Running Model for " + header[i])
					RunModel(modelParams, modelInput, fieldName)