import numpy as np
import pandas as pd
import random



def random_phrase():
    '''List of adjectives and nouns.
    Fuction will return 1 random item from each list'''

    # List of Adjectives
    adjectives = ['blue', 'large', 'grainy', 'substantial', 'potent', 'thermonuclear']

    # List of Nouns
    nouns = ['food', 'house', 'tree', 'bicycle', 'toupee', 'phone']

    # Returning one random adjective and one randon noun as a string together
    return f'{random.choice(adjectives)} {random.choice(nouns)}'

def random_float():
    '''Simple function that will give a random float rounded to 2 decimal places'''
    return round(random.uniform(.1, .9), 2)

def random_bowling_score():
    '''Simple function that will give a random interger between 0 and 300'''
    return random.choice(range(0,300))

def silly_tuple():
    '''A function to return a tuple of the random_phrase,
    random_float, and random_bowling_score function outputs'''
    return (random_phrase(), random_float(), random_bowling_score())
    
def silly_tuple_list(num_tuples):
    '''This function will create an empty list and run a for loop for how many time
    you want it to run. Each time it loops it will append 
    the list with the tupples created from silly_tuple'''
    
    # empty list
    silly_list = []

    # For loop to add tuples to empty list
    for x in range(num_tuples):
        silly_list.append(silly_tuple())

    # returning the list after it has been updated
    return silly_list
        
# Creating a small Data frame with 4 NaN values
df = pd.DataFrame(np.array([[1, np.nan, np.nan], [4, np.nan, 6], [np.nan, 8, 9]]),
                   columns=['a', 'b', 'c'])

def null_count(df):
    '''This fucntion will return the total number of Null values in a dataframe'''
    return df.isnull().sum().sum()




