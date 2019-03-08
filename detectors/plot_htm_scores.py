"""
Author: Christina Mao
Date Created: 22 February 2019
Description: Plot all csv files generated from htm_univariate.py in '/results' and saves them to '/plots'. 
Specify directory path  with _RESULTS_DIR
To-do: Fix Axes alignment if Y1 has 0s
To-do: Save as PDF instead of PNG
To-do: Subplot option  for same 
"""
import os
import pandas as pd
import plotly as py
import plotly.graph_objs as go 
import plotly.io as pio #To save static images

#If $Conda install -c plotly plotly.orca fails, specify the full path 
py.io.orca.config.executable = '/home/cmao/anaconda2/bin/orca' 

_RESULTS_DIR = os.getcwd() + '/results/20190220/'
_OUTPUT_DIR =  os.getcwd() + '/plots/20190220/'


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
	df = pd.read_csv(csvfile, sep=',')
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
		os.mkdir(_OUTPUT_DIR)
	os.chdir(_OUTPUT_DIR)
	# Create plots for all files in directory 
	for filename in os.listdir(_RESULTS_DIR):
		# If plot image not created yet
		if(not os.path.exists(_OUTPUT_DIR + filename + '.png')):
			PlotResults(_RESULTS_DIR + filename)
