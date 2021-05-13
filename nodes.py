import itertools
from svgwrite import *
from svgwrite.shapes import *
from svgwrite.container import *
from svgwrite.path import *
import random
import copy

GRID = 20
DIST = 25
OFFSET = DIST

SNAKES = 30

COLORS = ['9b59b6','3498db','2ecc71','1abc9c','f1c40f','e74c3c','e67e22']
COLORS = list(map(lambda x: '#'+x,COLORS))
nodes = None
l = None

MAX_LENGTH = 15

def RandomEmptyNode(overrides=[]):
	node= None
	while True:
		node = random.choice(l)
		if len(node.connections)==4 and not node in overrides:
			break
	return node

def findPaths(start,end,overrides=[]):
	if end in start.connections:
		return [[end]]
	else:
		options = []
		for connection in start.connections:
			if connection not in overrides:
				paths = findPaths(connection,end,[start]+overrides)
				if paths:
					options+=[[connection]+path for path in paths]
	return options

def getPath(start,end):
	paths = findPaths(start,end)
	paths.sort(key=lambda l:len(l))
	return paths[0]



class Point():
	def __init__(self,x,y):
		self.x =x
		self.y= y

	def t(self):
		return (self.x,self.y)

	def pixel(self):
		return ctp(self.t())

	def __sub__(self,other):
		return Point(self.x-other.x,self.y-other.y)

	def __add__(self,other):
		return Point(self.x+other.x,self.y+other.y)

	def __repr__(self):
		return f"P({self.x},{self.y})"

class Snake():
	RADIUS = 5
	WIDTH = 3
	CORNER = 0.3

	start = (0,0) # start coordinate
	color = None

	def __init__(self):
		self.path = []
		self.color = random.choice(COLORS)

		start = RandomEmptyNode()
		self.start = start.coords
		end = RandomEmptyNode([start])
		path = getPath(start,end)
		print(path)

		self.path = [node.coords for node in path]


	def svg(self):
		g = Group()
		if len(self.path)>0:
			path = Path([('M',self.start.pixel())],stroke=self.color,stroke_width=Snake.WIDTH,fill='none')

			deltas = [self.path[i]-self.path[i-1] for i in range(1,len(self.path))]

			#print(deltas)

			for point in self.path:
				path.push(('L',point.pixel()[0],point.pixel()[1]))

			border = copy.deepcopy(path)
			border.update({'stroke-width':Snake.WIDTH*2,'stroke':'#ffffff'})

			g.add(border)
			g.add(path)

			circle = Circle(self.start.pixel(),Snake.RADIUS,fill=self.color)
			g.add(circle)
		return g

class Node():
	coords=()
	connections = []

	def __init__(self,coords):
		self.coords=coords
		self.connections=[]

	def __repr__(self):
		return str(self.coords)


def ctp(coord):
	return (coord[0]*DIST+OFFSET,coord[1]*DIST+OFFSET)

def main():
	l = (GRID*DIST) + (OFFSET*2)
	dwg = Drawing('res.svg',height=l, width=l)
	gen_grid(GRID)

	snakes = [Snake() for i in range(SNAKES)]

	for s in snakes:
		dwg.add(s.svg())

	dwg.save()

def remove(node):
	for c in node.connections:
		if node in c.connections:
			c.connections.remove(node)
	l.remove(node)

def unlink(a,b):
	if a in b.connections:
		b.connections.remove(a)

	if b in a.connections:
		a.connections.remove(b)

def gen_grid(n):
	global l
	nodes = [[Node(Point(i,j)) for j in range(n+2)]for i in range(n+2)]
	for i in range(1,n):
		for j in range(2,n):
			cons = [
			nodes[i][j+1],
			nodes[i][j-1],
			nodes[i+1][j],
			nodes[i-1][j]
			]
			random.shuffle(cons)
			nodes[i][j].connections=cons
	l = [j for sub in nodes for j in sub]


main()