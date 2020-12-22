class Node:
    def __init__(self, airport, stage):
        self.airport = airport
        self.profit = None
        self.nextNode = None
        self.vertices = []
        self.stage = stage
