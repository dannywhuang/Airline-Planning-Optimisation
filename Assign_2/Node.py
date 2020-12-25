class Node:
    def __init__(self, airport, stageNumber):
        self.airport = airport
        self.profit = None
        self.nextNodeIATA = None
        self.nextNodeStage = None
        self.vertices = {}
        self.stageNumber = stageNumber
