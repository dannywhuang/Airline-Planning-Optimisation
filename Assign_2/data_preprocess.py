import pandas as pd
from math import cos, sin, asin, sqrt, pi
import numpy as np


HUB = 'CDG' # paris
YIELD_PER_RTK = 0.26 # euros
FUEL_COST = 1.42 # 1.42 usd/gallon in 2020 from ass. 1


def calculateRevenue(origin, destination, flow):
    dist = calculateDistance(origin, destination)
    revenue = YIELD_PER_RTK * dist * flow
    return revenue


def getLeaseCost(type):
    return fleet.loc['Lease Cost', type]


def calculateCost(origin, destination, type):
    dist = calculateDistance(origin, destination)

    speed = fleet.loc['Speed', type]
    fixedCost = fleet.loc['Fixed Operating Cost', type]
    costPerHour = fleet.loc['Cost per Hour', type]
    fuelCostParameter = fleet.loc['Fuel Cost Parameter', type]

    return fixedCost + costPerHour*(dist/speed) + fuelCostParameter*FUEL_COST/1.5*dist







airportData = loadAirports()
fleet = loadFleet()
demand = loadDemand()

