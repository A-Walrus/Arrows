import itertools
from svgwrite import *
from svgwrite.shapes import *
from svgwrite.container import *
from svgwrite.path import *
from svgwrite.text import *
import random
import copy
from math import *

GRID = 107
DIST = 20
OFFSET = DIST*2

SNAKES = 2

class CouldntCreate(Exception):
	pass


BG= '#111111'
COLORS = ['C2185B','1abc9c','2ecc71','3498db','9b59b6','16a085','27ae60','2980b9','8e44ad','f1c40f','e67e22','f39c12','c0392b','F06292']
# COLORS = [	'D84315','EF6C00','FF8F00','F9A825','9E9D24','558B2F','2E7D32','00695C','00838F','0277BD','1565C0','283593','4527A0','6A1B9A','AD1457','c62828']
COLORS = list(map(lambda x: '#'+x,COLORS))
nodes = None
l = None

MAX_LENGTH = 8
MIN_LENGTH = 3
dwg = None

def findConnected(start,connected = set(),draw=False): # not used
	if (len(start.connections)==0):
		print("wtf")
	global dwg
	connected.add(start)
	for c in start.connections:
		if c not in connected:
			if draw:
				print("line")
				dwg.add(Line(start=start.coords.pixel(),end=c.coords.pixel(),stroke='#ffffff',stroke_width=3))
			findConnected(c,connected)
	return connected

def RandomEmptyNode(start=None):
	if start:
		s= list(set(l) & findConnected(start))
	else:
		s = l

	node= None

	s = list(filter(lambda node: len(node.connections)==4 and node!=start and (not start or MIN_LENGTH<=(node.coords-start.coords).length()<=MAX_LENGTH) , s))
	try:
		return random.choice(s)
	except:
		raise CouldntCreate
	

def findPaths(start,end):
	paths = {}
	layer = [start]
	while end not in paths:
		new_layer=[]
		for node in layer:
			for con in node.connections:
				if con not in paths:
					paths[con]=node
					new_layer.append(con)
		layer=new_layer
		if layer==[]:
			dwg.add(Circle(start.coords.pixel(),Snake.RADIUS,fill='#ffffff'))
			dwg.add(Circle(end.coords.pixel(),Snake.RADIUS,fill='#ffffff'))
			findConnected(start,draw=True)
			return False

	path=[]
	pos = end
	while pos !=start:
		path.append(pos)
		pos = paths[pos]
	return path[::-1]

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

	def __mul__(self,other):
		return Point(self.x*other,self.y*other)

	def __repr__(self):
		return f"P({self.x},{self.y})"

	def __eq__(self,obj):
		return isinstance(obj, Point) and obj.x == self.x and obj.y==self.y

	def length(self):
		return abs(self.x)+abs(self.y)

	def angle(self):
		return atan2(self.y,self.x)

	def __hash__(self):
		return hash((self.x,self.y))

	def dist(self,other):
		res = sqrt((self.x-other.x)**2+(self.y-other.y)**2)
		return res

class Snake():
	RADIUS = 5
	WIDTH = 3
	CORNER = DIST/4
	TRI_H = 0.5
	TRI_W = 0.3

	start = (0,0) # start coordinate
	color = None

	def __init__(self):

		self.path = []
		self.color = random.choice(COLORS)

		start = None
		end = None
		path = None

		for i in range(100):
			start = RandomEmptyNode()
			end = RandomEmptyNode(start)
			path = findPaths(start,end)
			if path:
				break
			raise CouldntCreate
		else:
			raise CouldntCreate

		self.start = start.coords

		print(end,start)
		remove_node(end)
		remove_node(start)
		path.insert(0,start)
		for i in range(1,len(path)-1):
			n,c,p = path[i+1],path[i],path[i-1]
			unlink(c,n)
			if c.coords-p.coords!= n.coords-c.coords:
				remove_node(c)


		self.path = [node.coords for node in path]


	def svg(self):
		g = Group()
		if len(self.path)>0:
			path = Path([('M',self.start.pixel())],stroke=self.color,stroke_width=Snake.WIDTH,fill='none')

			deltas = [self.path[i]-self.path[i-1] for i in range(1,len(self.path))]

			commands=[]

			prev_delta = None
			i=0
			for i in range(len(self.path)):
				if 0<i<len(self.path)-1 and deltas[i-1] != deltas[i]:
					to = deltas[i-1]
					fr = deltas[i]
					pos = self.path[i]
					MAGIC = 0.552284749831*Snake.CORNER
					path.push(('L',pos.pixel()[0]-Snake.CORNER*to.x,pos.pixel()[1]-Snake.CORNER*to.y))
					target = (pos.pixel()[0]+Snake.CORNER*fr.x,pos.pixel()[1]+Snake.CORNER*fr.y)
					path.push(('C',pos.pixel()[0]-MAGIC*to.x,pos.pixel()[1]-MAGIC*to.y,pos.pixel()[0]+MAGIC*fr.x,pos.pixel()[1]+MAGIC*fr.y,target[0],target[1]))
					
					# direction = '+' if (to+fr).angle()>0 else '-'
					# path.push_arc(target,90,Snake.CORNER,False,direction,True)
				else:
					path.push(('L',self.path[i].pixel()[0],self.path[i].pixel()[1]))

			border = copy.deepcopy(path)
			border.update({'stroke-width':Snake.WIDTH*3,'stroke':BG})

			g.add(border)
			g.add(path)

			end = self.path[-1]
			forward = deltas[-1]*Snake.TRI_H
			side = Point(forward.y,forward.x)*(Snake.TRI_W/Snake.TRI_H)
			triangle = Path([('M',(end+side).pixel()),('L',(end+forward).pixel()),('L',(end-side).pixel())],fill=self.color)

			g.add(triangle)

			circle = Circle(self.start.pixel(),Snake.RADIUS,fill=self.color)
			g.add(circle)
		return g

class Node():
	coords=()
	connections = []

	def __init__(self,coords):
		self.coords=coords
		self.connections=[]
		self.paths={}

	def __repr__(self):
		return str(self.coords)

	def __eq__(self,obj):
		return isinstance(obj, Node) and obj.coords == self.coords and obj.connections==self.connections

	def __hash__(self):
		return hash(self.coords)

def ctp(coord):
	return (coord[0]*DIST+OFFSET,coord[1]*DIST+OFFSET)

def main():
	global dwg
	leee = (GRID*DIST) + (OFFSET*2)
	dwg = Drawing('D:/Users/Guy/my python/Snakes/v2/Arrows/res.svg',size = (leee,leee))
	dwg.add(dwg.rect(insert=(0, 0), size=('100%', '100%'), rx=None, ry=None, fill=BG))
	gen_graph(GRID)

	# Draw Dots
	debug = Group()
	for node in l:
		# dwg.add(Circle(node.coords.pixel(),1,fill="white"))
		debug.add(Text(f"({node.coords.x},{node.coords.y})",insert=node.coords.pixel(),fill='#ffffff',font_size='3px',stroke='none'))
	dwg.add(debug)

	try:
		while True:
			print("new snake")
			s = Snake()
			dwg.add(s.svg())
			
	except CouldntCreate:
		dwg.save()

def remove_node(node):
	for c in node.connections:
		unlink(node,c)

	if node in l:
		l.remove(node)

def unlink(a,b):
	if a in b.connections:
		b.connections.remove(a)

	if b in a.connections:
		a.connections.remove(b)

	if a in l and len(a.connections)==0:
		l.remove(a)

	if b in l and len(b.connections)==0:
		l.remove(b)


def gen_graph(n):
	global l
	global nodes
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

	# Turn into circle
	center = Point(GRID/2,GRID/2)
	to_remove = list(filter(lambda node: node.coords.dist(center)>(n)/2,l))
	for node in to_remove:
		remove_node(node)

main()