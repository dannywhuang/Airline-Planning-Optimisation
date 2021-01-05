class Route:
    def __init__(self, aircraftType, profit):
        self.aircraftType = aircraftType
        self.profit = profit
        self.routeNodesList = []
    def addRouteNode(self, routeNode):
        self.routeNodesList.append(routeNode)