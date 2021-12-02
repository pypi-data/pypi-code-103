# Build Person Class

# TODO:
# -pass in a census block and generate a human
# -age, gender and race for now
# ? how to determine race from median age... we have age and gender of can determine race from this?


class Person():
    """
    A basic person class to hold census distribution data
    """

    def __init__(self, uuid, gender_age=None, race=None, height=None, weight=None, census_block_group=None):
        self.baseline = { #sampleFromJointDistribution() https://data.census.gov/cedsci/table?q=United%20States&tid=ACSDP1Y2019.DP05
            'gender_age':           gender_age,
            'race':                 race,
            'height':               height, #meters
            'weight':               weight, #kg
            'census_block_group':   census_block_group,
            'uuid':                 uuid,
            'home_location':        None
        }
        self.activity = {
            'location':             None,
            'dwell':                None,
            'distance':             None,
            'travel_time':          None,
            'elapsed_time':         None
        }
        self.current_location =     None
        self.exposure = {}
        self.mobility = {}

        #Reinforcement Learning Parameters
        self.state =                None
        self.observation =          None
