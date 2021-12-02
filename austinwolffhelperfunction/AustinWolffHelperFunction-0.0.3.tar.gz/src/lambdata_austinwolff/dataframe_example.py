import pandas as pd

# An object once it has been created is called an instance
# The act of creating an object from a class constructor is called instantiation

# one instance of a dataframe object
df = pd.DataFrame({
    'a': [1,2,3],
    'b': [4,5,6]
})

# second instance of a dataframe object
df1 = pd.DataFrame({
    'a': [1,2,3],
    'b': [4,5,6]
})

# third instance of a dataframe object
df2 = pd.DataFrame({
    'a': [1,2,3],
    'b': [4,5,6]
})

# Class Variables are called "Attributes"
# Attributes do not use parentheses
print(df.shape) # -> (3, 2)
print(df.index)

# Class functions. Note how the parantheses invoke them. They are called "methods"
# print(df.drop())
print(df.describe())
print(df.head())