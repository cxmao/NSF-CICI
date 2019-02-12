#
#
#
#
import os
import csv
import yaml
from nupic.frameworks.opf.model_factory import ModelFactory

_CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

_MODEL_PARAMS_PATH = os.path.join(_CURRENTDIR, os.pardir, "params", "model.yaml")

print(_MODEL_PARAMS_PATH)


cpuDatapath = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.cpu"
dskDatapath = "/home/cmao/Repos/nsf-cici/data/collectl/kelewan-20190208.dsk"


def getData(datasetPath):
	with open(datasetPath) as openfile: 
		reader = csv.reader(openfile)
#		for x in openfile:
#			print(reader.next())

def createModel():
	with open(_PARAMS_PATH, "r") as f:
		modelParams = yaml.safe_load(f)
		return ModelFactory.create(modelParams)


def runModel(): 
	# Get Data
	cpuData = getData(cpuDatapath)
	

	#Results 
	results = []

	

if __name__ == "__main__": 
	runModel()	
