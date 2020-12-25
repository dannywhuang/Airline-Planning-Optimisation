import pandas as pd
from math import cos, sin, asin, sqrt, pi
import numpy as np
from Airport import Airport


class Airports:
    HUB = 'CDG'

    def __init__(self):
        self.data = pd.read_excel('data/airports.xlsx',index_col=0)
        self.IATAList = np.array(self.data.columns)
        self.airportsList = {}
        for i in self.IATAList:
            ap = self.data[i]
            self.airportsList[i] = Airport(i, ap['City'], ap['Latitude'], ap['Longitude'], ap['Runway'])


    def calculateDistance(self, Airport1, Airport2):
        if Airport1.IATA not in self.IATAList or Airport2.IATA not in self.IATAList:
            print("Error in calculateDistance: IATA does not exist")
            return

        if Airport1.IATA != self.HUB and Airport2.IATA != self.HUB: # if both are not the hub, calculate distance by considering going to the hub
            return self.calculateDistance(Airport1, self.airportsList[self.HUB]) + self.calculateDistance(self.airportsList[self.HUB], Airport2)
        else: # if one of the airports is the hub, then calculate distance once
            latitude1 = Airport1.latitude
            latitude2 = Airport2.latitude
            longitude1 = Airport1.longitude
            longitude2 = Airport2.longitude

            t1 = pow(sin((latitude1 - latitude2) / 2 * (pi / 180)), 2)
            t2 = cos(latitude1 * (pi / 180)) * cos(latitude2 * (pi / 180)) * pow(
                sin((longitude1 - longitude2) / 2 * (pi / 180)), 2)
            deltaSigma = 2 * asin(sqrt(t1 + t2))
            distance = 6371 * deltaSigma

            return distance