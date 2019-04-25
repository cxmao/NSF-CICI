"""
Author: Christina Mao
Date Created: 22 February 2019
Description: Plot all csv files generated from htm_univariate.py in '/results' and saves them to '/plots'. 
Specify directory path  with _RESULTS_DIR
To-do: Fix Axes alignment if Y1 has 0s
To-do: Subplot option  for sub fields i.e. cpu0
To-do: Highlight areas where globus transfers are occuring 
To-do: Highlight areas where attacks are occuring 
To-do: FindAnomalies
"""
import os
import pandas as pd
import plotly as py
import plotly.graph_objs as go 
import plotly.io as pio #To save static images
import numpy as np
import datetime

#If $Conda install -c plotly plotly.orca fails, specify the full path 
py.io.orca.config.executable = '/home/cmao/anaconda2/bin/orca' 

_DATE = 20190406
_INPUT_DIR = os.getcwd() + '/results/hping1/test/' + str(_DATE) +"/"
_OUTPUT_DIR = os.getcwd() + '/plots/hping1/test/' + str(_DATE) + "/"


_ALL = False
_FILENAME = 'Interrupts per Second_anomaly_scores_avg10s.csv'
_TESTING = True

if _TESTING == True: 
	_TESTTIME = "041819-22:33"
	_INPUT_DIR =  os.getcwd() + '/parameter-test/hping1/20190406/' + _TESTTIME + '/'
	_OUTPUT_DIR = _INPUT_DIR


class Highlight:
	def __init__(self, layout):
		self.layout = layout

	def update(self, xstart, xend, ymax):

		return

def Highlight(layout):
	layout.update(dict(shapes=[
		{
			'type': 'rect',
			# x-reference is assigned to the x-values
			#  'xref': 'x',
			# y-reference is assigned to the plot paper [0,1]
			#  'yref': 'paper',
			'x0': '2019-04-06 12:00:00',
			'y0': 0,
			'x1': '2019-04-06 12:15:00',
			'y1': ymax,  # Get max y-value
			'fillcolor': '#d3d3d3',
			'opacity': 0.5,
			'line': {
				'width': 0,
			}

		}

	]))
	return layout

def LoadData(filepath):
	try:
		assert(os.path.isfile(filepath))
	except:
		print(filepath + " does not exist")
	else:
		df = pd.read_csv(filepath, sep=',')
		df_clean = df.dropna(how='any')# Drop rows with any NaN values
		return df_clean


def FindAnomalies(df, threshold):
	""" 
	Description: 
	Parameters: 
		x <plotly.go data object> 
		threshold <int> 
	Returns: 
		trace - Return plotly trace with anomaly scores greater than threshold for each timestamp
	"""
	print df.shape[0]
	dfcolumns = df.columns
	print dfcolumns
	dfindex = df.index
	print dfindex

	newdf = pd.DataFrame(np.nan, index = dfindex, columns = dfcolumns)
	print newdf.loc[0]
	for index, row in df.iterrows():
		return



def PlotResults(csvfile):
	"""
	Description: Takes a @csvfile generated from htm_univariate.py and plots its on two Y-axes. 
	Plots are saved as PNG files to current directory
	Parameters: 
		csvfile <string> full file path
	Returns: 
		Null
	"""
	# Load CSV file with Pandas dataframe
	try:
		 os.path.exists(csvfile)
	except  ValueError as error:
		print ("No such directory" + _INPUT_DIR)

	df = LoadData(csvfile)
	keys = df.keys()
	# Get field name
	f = open(csvfile)
	lines = f.readline()
	header = lines.split(',')

	#Get max y-value for highlight
	ymax = df[keys[1]].max()
	print ymax

	print ('Plotting ' + header[1])

	# Double Axes
	trace1 = go.Scatter(
					x=df['timestamp'],
					y=df[keys[1]],
					name=keys[1]
				)
	trace2 = go.Scatter(
					x=df['timestamp'],
					y=df[keys[2]],
					name='Anomaly Score',
					yaxis='y2',
					mode='lines',
					opacity=0.5
				)

	data = [trace1, trace2]
	layout = go.Layout(
		title= "HTM Anomaly Scores",
		xaxis=dict(
			title='Date & Time'
		),
    	yaxis=dict(
	        title=header[1]
    	),
   		yaxis2=dict(
	        title='Anomaly Index',
	        titlefont=dict(
            color='rgb(148, 103, 189)'
	        ),
	        tickfont=dict(
	            color='rgb(148, 103, 189)'
	        ),
	        overlaying='y',
	        side='right',
			rangemode='tozero',  # align y-axes
		),
		width = 1900,
		height = 1200,
		#autosize=False,
	)
	
	#Highlight(layout)
	#To-Do: Highlight timestamps where transfer occurred
	layout.update(dict(shapes = [
		{
			'type': 'rect',
            # x-reference is assigned to the x-values
          #  'xref': 'x',
            # y-reference is assigned to the plot paper [0,1]
          #  'yref': 'paper',
            'x0': '2019-04-06 12:00:00',
            'y0': 0,
            'x1': '2019-04-06 12:15:00',
            'y1': ymax, #Get max y-value
            'fillcolor': '#d3d3d3',
            'opacity': 0.5,
            'line': {
                'width': 0,
            }

		}

	]))
	
	fig = go.Figure(data=data, layout=layout)
	# Generate HTML file and view in browser
	py.offline.plot(fig, filename= keys[1] + '.html', auto_open=False)

	if _TESTING == True: 
		pio.write_image(fig, _TESTTIME + _FILENAME + '.svg')
		pio.write_image(fig, _TESTTIME + _FILENAME + '.pdf')
		layout = go.Layout(autosize=True)
		pio.write_image(fig, _TESTTIME + _FILENAME + '.png')
	else:
		# Save file
		pio.write_image(fig, keys[1] + '.svg')
		pio.write_image(fig, keys[1] + '.pdf')
		layout = go.Layout(autosize=True)
		pio.write_image(fig, keys[1] + '.png')
	return 



if __name__ == '__main__':
	# Create directory to store plot images
	if not os.path.exists(_OUTPUT_DIR):
		os.makedirs(_OUTPUT_DIR)
	os.chdir(_OUTPUT_DIR)

	# Check input direcotry 
	try: 
		 os.path.exists(_INPUT_DIR)
	except  ValueError as error: 
		print ("No such directory" + _INPUT_DIR)

	if _ALL:
		# Create plots for all files in directory 
		for filename in os.listdir(_INPUT_DIR):
			# If plot image not created yet
			if(not os.path.exists(_OUTPUT_DIR + filename + '.png')):
				PlotResults(_INPUT_DIR + filename)

	if not _ALL: 
		PlotResults(_INPUT_DIR + _FILENAME)
	#	PlotAnnotatedResults(_INPUT_DIR + _FILENAME)
