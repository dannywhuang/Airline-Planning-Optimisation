from math import floor
from Node import Node

class Stage:
    def __init__(self, time):
        self.time = time
        self.nodesList = {}
        self.binNumber = 29 if time == 120 else floor(time/4)
    def addNode(self, airport):
        self.nodesList[airport.IATA] = Node(airport, self)