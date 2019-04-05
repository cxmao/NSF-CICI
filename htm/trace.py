import plotly.graph_objs as go 

class CustomTrace:
	def __init__ (self, x, y, name, axis=None, mode = None, opacity = None):
		self.x = []
		self.y = []
		self.name = 'name'
		self.axis = 'y'
		self.mode = 'lines'
		self.opacity = 1


	def create_obj(self):
		go.Scatter(
			x =  self.x,
			y = self.y,
			name = self.name,
			yaxis = self.axis,
			mode = self.mode,
			opacity = self.opacity
			)

	def set_xy(self, x, y):
		self.x = x
		self.y = y

	def set_name (name):
		self.name = name

	def set_axis(self, xaxis, yaxis):
		self.xaxis = xaxis
		self.yaxis = yaxis

	def set_mode (self, mode):
		self.mode = mode

	def  set_opacity(self, opacity):
		self.opacity = opacity


class CustomLayout: 
	def __init__ (self, numPlots ):
		self.numPlots = 2
		self.title = 'Title'
		self.xaxis = dict(
			domain=[0,100],
			title='Xaxis'
			)
		self.yaxis = dict(
			domain=[0,100],
			title='Yaxis'
			)
		self.yaxis2 = dict(
			domain=[0,100],
			title='Yaxis2',
			overlaying='y',
			side= 'right'
			)



	def create_layout(self):
		go.Layout(

			)