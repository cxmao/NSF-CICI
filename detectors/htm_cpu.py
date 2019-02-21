# Author: Christina Mao 
# Date: 14 February 2019
# Uses the Nupic Online Prediction Framework (OPF) API
# Source code: https://github.com/numenta/nupic/blob/master/examples/opf/clients/hotgym/anomaly/hotgym_anomaly.py
# Description: 
# 
# To-do: Add control for field selection 
# To-do: Unzip file and stream 
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

# Nupic OPF
import base_model_params as mp
from nupic.frameworks.opf.model_factory import ModelFactory

#--------------------------------------------------------------------------------------------------------
# System variables
_LOGGER = logging.getLogger(__name__)
_OUTPUT_PATH = "anomaly_scores.csv"


# Data File Paths 
_BASE_MODEL_PARAMS_PATH = os.getcwd() + "/base_model_params.py"
_CPU_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.cpu"
_DISK_DATA_PATH = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.dsk"

# Model variables 
_FIELD_SELECTOR = [13, 25, 37, 49, 61, 73, 85] #Select based on Collectl log headers

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
		field - <string> Field name taken from Collectl Log 
	Returns:
		dictdump - <dict> 

	"""
	metric = "testmetric"

#	copyfile(_BASE_MODEL_PARAMS_PATH, filename)

	#Create a new Python file 
	with open(filename, "w+") as f: 
		data = json.dumps(mp.MODEL_PARAMS, sort_keys=False, indent=4) #Convert python object to a serialized JSON string 
		#Modify parameters in the new file
		temp_data = Template(data)
		final = temp_data.substitute(metricname = metric,
										fieldname=field)
		# Write as a dictionary to load into CreateModel()
		dictdump = json.loads(final)

		# Write JSON as a Python Object to file 
		f.write("MODEL_PARAMS = ")
		f.write(final)
	#Save and close file 
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
		headers - <list> 
	    modelInput - <list of dicts> 
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
	Parameters: 
		data - <list of dict> 
		fieldname - <string>

	Returns: 
		None
	"""
	model = CreateModel(params)
	model.enableInference({"predictedField": field}) #Use the field name, not the encoder name
	csvWriter = csv.writer(open(field + "_anomaly_scores.csv","wb"))
	csvWriter.writerow(["timestamp", field, "anomaly_score"])

	# Offline Results
	results = []
	for i in range(len(data[1])):
		results.append(model.run(data[1][i]))
		# Append Anomaly Score and write out results to CSV file 
		anomalyScore = results[i].inferences['anomalyScore']
		csvWriter.writerow([data[1][i]['timestamp'], data[1][i][field],anomalyScore]) 
	print ("Results written to " + os.getcwd() + "/" + field + "_anomaly_scores.csv")
	"""
	# Logger
	 	if anomalyScore > _ANOMALY_THRESHOLD:
	      _LOGGER.info("Anomaly detected at [%s]. Anomaly score: %f.",
	                    result.rawInput["timestamp"], anomalyScore)
	"""
	return 0

	# Online Results

def PlotResults(csvfile):
	"""
	To-do: Overlap anomaly scatter plot denoting peaks with line chart
	"""
	filePath = os.getcwd() + "/" + csvfile
	print filePath
	# Load with Numpy 
	plt.title('CPU Anomaly Scores')
	plt.xlabel('time [s]')
	plt.ylabel('CPU Total Interrupts')
	
	with open(filePath, 'r') as f:
	    reader = csv.reader(f, delimiter=',')
	    # get header from first ro
	    headers = next(reader)
	    # get all the rows as a list
	    data = list(reader)
	    # transform data into numpy array
	    #data[1:2] = np.array(data[1:2]).astype(float)
	    print(data[1])
	    

	# Load with Pandas Dataframe
	'''
	ts = pd.Series.from_csv(filePath, header=0)
	print(ts.head())
	print(type(ts))
	'''
	df = pd.read_csv(filePath, sep=',')
	print(df.head())
	print(type(df['timestamp']))
	ax = plt.gca()
	df.plot(x='timestamp', title='CPU Total Interrupts', grid=True, ax=ax)
	#df.plot(kind='scatter', x='timestamp', y='anomaly_score', title='CPU Total Interrupts', grid=True, ax=ax)
	#cpu_d = cpu_df.cumsum()
	#print (cpu_df['total_utilization%'])
	#plt.figure()
	#cpu_df.plot()
	plt.show()
	# Save Plot to File

	return 


if __name__ == "__main__":
	for i in range(len(_FIELD_SELECTOR)):
		modelInput = GetData(_CPU_DATA_PATH, _FIELD_SELECTOR[i])
		fieldName = GetFieldName(modelInput[0],_FIELD_SELECTOR[i])
		modelParams = SetModelParams(fieldName + ".py", fieldName)
		RunModel(modelParams,modelInput, fieldName)
		#PlotResults(_OUTPUT_PATH)
