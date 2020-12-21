class Aircraft:
    EXTRA_TAT_BEFORE = 15
    EXTRA_TAT_AFTER = 15

    def __init__(self, type, speed, capacity, TAT, maxRange, runwayRequired, leaseCost, fixedCost, costPerHour, fuelCostParam):
        self.type = type
        self.speed = speed
        self.capacity = capacity
        self.TAT = TAT + self.EXTRA_TAT_AFTER + self.EXTRA_TAT_BEFORE
        self.maxRange = maxRange
        self.runwayRequired = runwayRequired
        self.leaseCost = leaseCost
        self.fixedCost = fixedCost
        self.costPerHour = costPerHour
        self.fuelCostParam = fuelCostParam