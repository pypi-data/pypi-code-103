# Build population generator class
from scipy.stats import multinomial
import pandas as pd
from poppygen import Person


class PopulationGenerator():
    """
    A population generator class based on census distribution data

    Parameters:
        census_block_group (list-like) optional: 1 or more census block groups in a list, can be exact cbg or parital to match all 'like'
        year (int): 4 digit integer year

    Returns:
        PopulationGenerator Object: Returning value
    """

    def __init__(self, acs_df, poi_df=None, census_block_group=None, year=0000, like=False):
        self.census_block_group = census_block_group
        self.year = year
        # TODO: house df of interest here? or have a data class, that prepares and holds data
        # self.current_data_df
        # self.current_meta_df
        self.gender_age_df = pd.DataFrame()
        self.gender_age_labels = list()
        self._count = -1
        self.acs_df = acs_df #american community survey data (acs)
        self.poi_df = poi_df          #safegraph point of interest data (poi)
        #self.lbs_df = lbs_df                   #locatin based services data (lbs)

    @property
    def count(self):
        """Getter Method"""
        self._count += 1
        return self._count

    # @count.setter
    # def count(self):
    #     self._count =

    def select_data(self):
        pass

    def clean_data(self):
        pass

    def get_gender_age(self, census_block_group=None):
        # get only gender and age
        gender_age_df = self.acs_df.filter(like="SEX_BY_AGE") #TODO: Missing preprocessed current dataframe
        # print(gender_age_df)

        # get labels for data
        gender_age_labels = list(gender_age_df.columns)

        # add census_block_group to labels so we can filter the df and use census_block_group as index
        gender_age_labels.insert(0, "census_block_group")
        # display(gender_age_labels)

        # use census_block_group as index
        gender_age_df = self.acs_df.filter(gender_age_labels)
        gender_age_df.set_index("census_block_group", inplace=True)
        # display(gender_age_df)

        # make labels a one-to-one map to label gender_age_probList
        remove_labels = ["census_block_group", "SEX_BY_AGE_Total_population_Total_Male",
                         "SEX_BY_AGE_Total_population_Total_Female", "SEX_BY_AGE_Total_population_Total"]
        for d in remove_labels:
            gender_age_labels.remove(d)
        # display(gender_age_labels)

        # build probility list for multinomial distribution
        gender_age_probList = list()
        for x in gender_age_labels:
            # print(x)
            gender_age_probList.append(
                gender_age_df.at[census_block_group, x] / gender_age_df.SEX_BY_AGE_Total_population_Total.at[
                    census_block_group])

        # must be same length
        assert (len(gender_age_probList) == len(gender_age_labels))
        self.gender_age_df = gender_age_df
        self.gender_age_labels = gender_age_labels
        return gender_age_probList, gender_age_labels

    def generate_population(self, population_size, census_block_group=None, like=False):
        """
        Generators population based on params

        Parameters:
            population_size (int): population size of each census_block_group in list
            census_block_group (list-like) optional: census block groups, overide class self.census_block_group
            like (bool) optional: use fuzzy regex match on provided cbgs

        Returns:
            population (list): Returns a list of Persons() generated
        """
        population = list()

        if like is True:
            # create a list... from 'like' first numbers in census_block_group in gender_age_df... scoop for gender_age_df is in other function
            pass
        if census_block_group is None and self.census_block_group is None:
            print("Please Provide census_block_group Param")
        elif census_block_group is None:
            cbg = self.census_block_group
        else:
            cbg = census_block_group

        for c in cbg:
            gender_age_probList, gender_age_labels = self.get_gender_age(census_block_group=c)
            rv_gender_age = multinomial.rvs(population_size, gender_age_probList)
            print(
                f'\n[i] Generated Population:\n{rv_gender_age}\n[i] Labels:\n{gender_age_labels}\n[i] Block Group:\n{c}\n[i] Probibility List:\n{gender_age_probList}\n[i] Population Size:\n{population_size}\n')
            for i, x in enumerate(rv_gender_age):
                [population.append(Person(gender_age=gender_age_labels[i], census_block_group=c, uuid=self.count)) for _ in range(x)]

            # assert(len(population) == population_size)
        print(len(population))
        return population

    def generate_activity(self, population=list):
        # take in a list of persons, in a population list
        # read in pattern data
        # assign each person a
        if self.poi_df is None:
            print("POI Dataset Not Available")
            return
        #Assign activity within perons census block group
        for person in population:
            poi = self.poi_df[self.poi_df.poi_cbg == person.baseline["census_block_group"]].sample() #TODO: Missing preprocessed mobility dataframe
            person.activity["location"] = poi.street_address.to_string(index=False) + " " + poi.city.to_string(index=False) \
                                          + " " + poi.region.to_string(index=False) + " " + poi.postal_code.to_string(index=False)
