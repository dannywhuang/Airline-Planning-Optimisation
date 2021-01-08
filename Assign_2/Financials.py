from Airports import Airports
from Fleet import Fleet

class Financials:
    YIELD_PER_RTK = 0.26  # euros
    FUEL_COST = 1.42  # 1.42 usd/gallon in 2020 from ass. 1

    def __init__(self, airportsFileName, fleetFileName):
        self.airports = Airports(airportsFileName)
        self.fleet = Fleet(fleetFileName)

    def calculateRevenue(self, airport1, airport2, flow):
        dist = self.airports.calculateDistance(airport1, airport2)
        revenue = self.YIELD_PER_RTK * dist * flow/1000
        return revenue

    def getLeaseCost(self, type):
        return self.fleet.aircraftList[type].leaseCost

    def calculateCost(self, airport1, airport2, type):
        dist = self.airports.calculateDistance(airport1, airport2)
        speed = self.fleet.aircraftList[type].speed
        fixedCost = self.fleet.aircraftList[type].fixedCost
        costPerHour = self.fleet.aircraftList[type].costPerHour
        fuelCostParameter = self.fleet.aircraftList[type].fuelCostParam

        return fixedCost + costPerHour*(dist/speed) + fuelCostParameter*self.FUEL_COST/1.5*dist


