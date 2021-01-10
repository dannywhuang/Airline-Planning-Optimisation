from Airports import Airports
from Fleet import Fleet
from Financials import Financials
from KPI_store import KPI_store
import pickle




Fleet = Fleet('fleet.xlsx')
airports = Airports('airports.xlsx')
Financials = Financials('airports.xlsx','fleet.xlsx')


ask_ac = {}
time_ac = {}
KPI = {}


def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


routes = load_obj("routesList")

for ii, route in enumerate(routes):
    KPI_ac = {}
    ask_sum = 0
    time_sum = 0
    routeNodesList = route.routeNodesList
    type = route.aircraftType
    flightCapacity = Fleet.aircraftList[type].capacity
    speed          = Fleet.aircraftList[type].speed
    TAT            = Fleet.aircraftList[type].TAT

    for i in range(len(routeNodesList) - 1):
        origin = routeNodesList[i].IATA
        destination = routeNodesList[i + 1].IATA
        cargo       = routeNodesList[i].cargo
        airportsList = airports.airportsList
        origin_dat   = airportsList[origin]
        destination_dat = airportsList[destination]
        if origin != destination:
                distance = airports.calculateDistance(origin_dat, destination_dat)
                totalTravelTime = routeNodesList[i + 1].time - routeNodesList[i].time
                #totalTravelTime = distance/speed + TAT/60
                RTK        = cargo/1000*distance
                ASK        = flightCapacity/1000*distance
                flightRevenue = Financials.calculateRevenue(origin_dat, destination_dat, cargo)
                flightCost = Financials.calculateCost(origin_dat, destination_dat, type)
                profit     = flightRevenue-flightCost
                RASK       = ASK*flightRevenue
                CASK       = ASK*flightCost
                ask_sum    = ask_sum + ASK
                time_sum   = time_sum + totalTravelTime
                KPI_ac[origin,destination] = KPI_store(ASK,RTK, CASK, RASK,profit)
                #if ii == 3:
                #    print(cargo)

    KPI[ii,type]     = KPI_ac
    ask_ac[ii,type]  = ask_sum
    time_ac[ii,type] = time_sum

