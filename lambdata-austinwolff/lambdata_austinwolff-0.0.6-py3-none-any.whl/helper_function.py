import numpy as np
import pandas as pd

def say_hello():
    print(np.array(["hello"]))
    return None

def random_phrase():
    adjectives = np.array(['blue', 'large', 'grainy', 
                        'substantial', 'potent', 'thermonuclear'])
    nouns = np.array(['food', 'house', 'tree', 'bicycle', 
                    'toupee', 'phone'])
    x = np.random.choice(adjectives)
    y = np.random.choice(nouns)
    return x + ' ' + y

def random_float(min_val, max_val):
    return round(np.random.uniform(low=min_val, high=max_val), 2)

def random_bowling_score():
    return np.random.randint(0, 300)

def silly_tuple():
    return (random_phrase(), random_float(1, 5), random_bowling_score())

def silly_tuple_list(num_tuples):
    return [silly_tuple() for i in range(num_tuples)]

def rem_outlier(df):
    for col in df.columns:
        upper_qr = np.percentile(df[col], 75)
        lower_qr = np.percentile(df[col], 25)
        iqr = (upper_qr - lower_qr) * 1.5
        upper_bound = upper_qr + iqr
        lower_bound = lower_qr - iqr
        print(upper_qr)
        print(upper_bound)
        for x in df.index:
            print(x)
            print(df.at[x, col])
            print(df[col])
            if (df.at[x, col] < lower_bound) or (df.at[x, col] > upper_bound):
                df.drop(x, inplace=True)
    return df



# TESTING
# print(random_phrase())
# print(random_float(3.0, 13.0))
# print(random_bowling_score())
# print(silly_tuple())
# print(silly_tuple_list(3))


# df = pd.DataFrame(
#     data={
#         'A':[9,3,6,3],
#         'B':[1,850,0,2],
#         'C':[2,5,8,1]
#     }
# )
# print(rem_outlier(df))