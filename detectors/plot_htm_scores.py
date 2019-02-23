"""
Author: Christina Mao
Date Created: 22 February 2019
Description: Plot all csv files generated from htm_univariate.py in '/results' and saves them to '/plots'
"""
import os
import pandas as pd
import plotly as py
import plotly.graph_objs as go 
import plotly.io as pio #To save static images

#If $Conda install -c plotly plotly.orca fails, specify the full path 
py.io.orca.config.executable = '/home/cmao/anaconda2/bin/orca' 

_RESULTS_DIR = os.getcwd() + '/results'


def PlotResults(csvfile):
	"""-
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
		title= "Hierarchical Temporal Memory Anomaly Scores",
		xaxis=dict(
			title='Date & Time'
		),
    	yaxis=dict(
	        title='KBytes Written'
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
	py.offline.plot(fig, filename= keys[1], auto_open=True) # View plot in browser
	# Save as PNG
	pio.write_image(fig, keys[1] + '.png')
	return 


def main():
	# Create directory to store plot images
	if not os.path.exists('plots'):
		os.mkdir('plots')
	os.chdir('plots')
	# Create plots for all files in directory 
	for filename in os.listdir(_RESULTS_DIR):
		PlotResults(_RESULTS_DIR + "/" + filename)


if __name__ == '__main__':
	main()