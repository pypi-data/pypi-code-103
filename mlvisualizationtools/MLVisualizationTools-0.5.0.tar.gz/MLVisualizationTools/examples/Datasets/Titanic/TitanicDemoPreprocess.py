from MLVisualizationTools.backend import fileloader
import pandas as pd

# This code was used to prep the training data for the demos based on the titanic dataset
# The orig file was left in train_orig.csv
# The modified file was moved to train.csv
# All operations performed are standard preprocessing

def main():
    df = pd.read_csv(fileloader('examples/Datasets/Titanic/train_orig.csv'))
    df.drop(['PassengerId', 'Name', 'Ticket', 'Cabin'], axis=1, inplace=True) #these cols don't have much useful data
    df['Age'].fillna(df['Age'].mean(), inplace=True) #this data has lots of nan values
    df = df[df['Embarked'].notna()] #this col is only missing two values
    df["Embarked"].replace({"C": 0, "S": 1, "Q": 2}, inplace=True) #numerical values are better for training
    df['Sex'].replace({"male": 0, "female": 1}, inplace=True)
    df.to_csv(fileloader('examples/Datasets/Titanic/train.csv'), index=False)

if __name__ == '__main__':
    main()