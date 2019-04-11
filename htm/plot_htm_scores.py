"""
Author: Christina Mao
Date Created: 22 February 2019
Description: Plot all csv files generated from htm_univariate.py in '/results' and saves them to '/plots'. 
Specify directory path  with _RESULTS_DIR
To-do: Fix Axes alignment if Y1 has 0s
To-do: Subplot option  for sub fields i.e. cpu0
"""
import os
import pandas as pd
import plotly as py
import plotly.graph_objs as go 
import plotly.io as pio #To save static images

#If $Conda install -c plotly plotly.orca fails, specify the full path 
py.io.orca.config.executable = '/home/cmao/anaconda2/bin/orca' 

_DATE = 20190406
_INPUT_DIR = os.getcwd() + '/results/hping1/nab/' + str(_DATE) +"/"
_OUTPUT_DIR = os.getcwd() + '/plots/hping1/nab/' + str(_DATE) + "/"


def LoadData(filepath):
	try:
		assert(os.path.isfile(filepath))
	except:
		print(filepath + " does not exist")
	else:
		df = pd.read_csv(filepath, sep=',')
		df_clean = df.dropna(how='any')# Drop rows with any NaN values
		return df_clean


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
	df = LoadData(csvfile)
	keys = df.keys()

	# Get field name
	f = open(csvfile)
	lines = f.readline()
	header = lines.split(',')
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
					mode='lines+markers',
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
	        side='right'
		)
	)
	fig = go.Figure(data=data, layout=layout)
	# Generate HTML file and view in browser
	py.offline.plot(fig, filename= keys[1] + '.html', auto_open=False) 
	# Save as PNG file
	pio.write_image(fig, keys[1] + '.pdf')
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

	# Create plots for all files in directory 
	for filename in os.listdir(_INPUT_DIR):
		# If plot image not created yet
		if(not os.path.exists(_OUTPUT_DIR + filename + '.png')):
			PlotResults(_INPUT_DIR + filename)
