class RouteNode:
    def __init__(self, IATA, time, profitLeft,cargo, stageNumber, binNumber):
        self.IATA = IATA
        self.time = time
        self.profitLeft = profitLeft
        self.cargo      = cargo
        self.stageNumber = stageNumber
        self.binNumber = binNumber

