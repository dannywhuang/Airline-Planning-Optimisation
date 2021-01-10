import pickle
from math import ceil

def save_obj(obj, name ):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)



from Airports import Airports
from Fleet import Fleet
from Demand import Demand
from Stage import Stage

Airports = Airports('airportsVerification.xlsx')
Demand = Demand('demandVerification.xlsx')
Fleet = Fleet('fleetVerification.xlsx')

airportsList = Airports.airportsList

STAGE_RESOLUTION = 6 # minutes
TOTAL_HOURS = 24# fill in how many hours

numberOfStages = int(TOTAL_HOURS*60 / STAGE_RESOLUTION + 1)


for type, aircraft in Fleet.aircraftList.items():
    print("Aircraft type: ", type)
    stagesList = [None] * numberOfStages
    # create last stage and add HUB node
    airportHUB = airportsList[Airports.HUB]
    lastStage = Stage(TOTAL_HOURS, numberOfStages-1)
    lastStage.addNode(airportHUB)
    stagesList[-1] = lastStage

    print("Creating stages and nodes...")
    # create other stages
    for i in range(1, numberOfStages):
        stageTime = TOTAL_HOURS-i*0.1

        stageNumber = numberOfStages - i - 1
        newStage = Stage(stageTime, stageNumber)
        stagesList[stageNumber] = newStage
        # for each stage create airport nodes
        newStage.addNode(airportHUB)
        for IATA, airport in Airports.airportsList.items():
            # only add airport nodes to stage that have the runway required
            if airport.runway > aircraft.runwayRequired:
                # only add airport if you can still reach HUB before end of day 5

                if (Airports.calculateDistance(airport, airportHUB)/aircraft.speed + aircraft.TAT/60) < TOTAL_HOURS-stageTime:
                    newStage.addNode(airport)

    # start creating vertices
    print("Creating vertices...")
    # iterate over all stages starting from last stage
    for i in range(len(stagesList)):

        stageNumber = numberOfStages - i - 1
        currentStage = stagesList[stageNumber]
        if i%10==0:
            print('Current stage', i)
        # iterate over all nodes in current stage
        for IATA, currentNode in currentStage.nodesList.items():

            # if current node is the hub, consider all demands departing from hub
            if IATA == Airports.HUB:
                currentAirportDemand = Demand.data.loc[Demand.data['From'] == Airports.HUB]
            # if current node is not hub only consider demands that arrive at the hub
            else:
                currentAirportDemand = Demand.data.loc[(Demand.data['From'] == IATA) & ((Demand.data['To'] == Airports.HUB) | (Demand.data['To'] == IATA))]

            # iterate over all possible destinations from current airport node
            for index, row in currentAirportDemand.iterrows():
                # current destination
                currentDestinationIATA = row['To']
                destinationAirport = airportsList[currentDestinationIATA]

                # travel time from origin to destination airport
                totalTravelTime = Airports.calculateDistance(currentNode.airport, destinationAirport) / aircraft.speed + aircraft.TAT / 60

                # next stage number where the destination airport can be reached
                diffStageNumber = int(ceil((totalTravelTime*60)/STAGE_RESOLUTION))
                nextStageNumber = stageNumber + 1 if currentNode.airport.IATA == currentDestinationIATA else stageNumber + diffStageNumber

                # if stage number is within the 5 days and if the airport node exists in that stage
                if (nextStageNumber <= numberOfStages-1 and currentDestinationIATA in stagesList[nextStageNumber].nodesList):
                    # add airport IATA as key and stage number as value
                    currentNode.vertices[destinationAirport.IATA] = nextStageNumber

    # save a stagesList for each aircraft type
    save_obj(stagesList, type+'Verification')