from Airports import Airports
from Fleet import Fleet
from Financials import Financials
from KPI_store import KPI_store
import pickle


def load_obj(name ):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)


routes = load_obj("routes")
type  = routes[0].aircraftType

print("AC type:", type)
print('Time', '  origin', '  destination', ' cargo')

for i in range(len(routes[0].routeNodesList)-1):
    time   = routes[0].routeNodesList[i].time
    cargo  = routes[0].routeNodesList[i].cargo
    origin = routes[0].routeNodesList[i].IATA
    destination = routes[0].routeNodesList[i+1].IATA
    if origin != destination:
        print(round(time, 1), '  ', origin, '   ', destination, "        ", cargo)



Fleet = Fleet()
airports = Airports()
Financials = Financials()

ask_ac = {}
time_ac = {}
KPI = {}
KPI_ac = {}

for type, aircraft in Fleet.aircraftList.items():
    ask_sum = 0
    time_sum = 0
    # array of airports (route)
    list_routs = None
    # cargo associated to each route
    cargo_l = None


    flightCapacity = Fleet.aircraftList[type].capacity
    # for i in range(len(list_routs)):
    #     origin = i
    #     destination = i+1
    #     distance = airports.calculateDistance(origin, destination)
    #     totalTravelTime = distance / aircraft.speed + aircraft.TAT / 60
    #     cargo    = cargo_l(i)
    #     RTK      = cargo/1000*distance
    #     ASK      = flightCapacity*distance
    #     flightRevenue = Financials.calculateRevenue(origin, destination, cargo)
    #     flightCost = Financials.calculateCost(origin, destination, type) if origin != destination else 0
    #     RASK       = ASK*flightRevenue
    #     CASK       = ASK*flightCost
    #     ask_sum+=ask_sum
    #     time_sum+=time_sum
    #     KPI_ac[origin,destination] = KPI_store(ASK,RTK, CASK, RASK)
    # KPI[type]     = KPI_ac
    # ask_ac[type]  = ask_sum
    # time_ac[type] = time_sum

