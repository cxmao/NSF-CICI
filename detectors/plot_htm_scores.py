import os
import pandas as pd
import plotly as py
import plotly.io as pio #To save static images
import cufflinks as cf #if using Plotly Pandas API
import plotly.graph_objs as go 

#To-do:

def PlotResults(csvfile):
	"""
	Description: 
	Parameters: 
		csvfile <string> full file path
	Returns: 
	"""

	# Load with Pandas Dataframe
	df = pd.read_csv(csvfile, sep=',')
	print(df.head())


	# With Plotly 
	'''
	py.offline.plot({
			"data": [
				go.Scatter(
					x=df['timestamp'],
					y=df['[DSK:sda]WKBytes']
				)
			]
		}, auto_open=True)
	'''

	# Double Y-axis with Pandas
	'''
	fig1 = df.iplot(columns=['timestamp', '[DSK:sda]WKBytes'], kind='bar', asFigure=True)
	fig2 = df.iplot(columns=['timestamp', 'anomaly_score'], 
		 secondary_y=['timestamp', 'anomaly_score'], asFigure=True)
	fig2['data'].extend(fig1['data'])
	py.iplot(fig2, filename='results/plots/multiple_yaxis')
	'''


	# Double Y-axis Python
	trace1 = go.Scatter(
					x=df['timestamp'],
					y=df['[DSK:sda]WKBytes'],
					name='[DSK:sda]WKByte',
				)
	trace2 = go.Scatter(
					x=df['timestamp'],
					y=df['anomaly_score'],
					name='Anomaly Score',
					yaxis='y2',
					mode='lines+markers',
					opacity=0.5
				)

	data = [trace1, trace2]
	layout = go.Layout(
		title='Double Y Axis Example',
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
	py.offline.plot(fig, filename='multiple_yaxis', auto_open=True)

	#Create directory to store plot images
	if not os.path.exists('plots'):
		os.mkdir('plots')
	# Save as PNG
	#pio.write_image(fig, 'plots/multiple_yaxis.png')

	return 

if __name__ == '__main__':
	PlotResults("/home/cmao/Repos/nsf-cici/detectors/results/[DSK:sda]WKBytes_anomaly_scores.csv")