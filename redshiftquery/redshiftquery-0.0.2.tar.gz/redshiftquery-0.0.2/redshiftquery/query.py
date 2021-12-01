
#%% Imports
import redshift_connector
import keyring
import pandas as pd
from datetime import datetime, date, time, timedelta
import os

#Helper funtion for managing SQL files
def get_dir() -> str:
    return os.path.dirname(os.path.realpath(__file__))


#%% Function for Creating a Connection
def createconnection():
    """
    Returns the connection for Helios Redshift instance
    """
    
    #Keyring used to store all info
    #To Do: Consider all the cases where users may have multiple Servers and databases
    host = keyring.get_password('Redshift', 'Host')
    database = keyring.get_password('Redshift', 'Database')
    username = keyring.get_password('RedShift', 'Username')
    password = keyring.get_password('RedShift', 'Password')
    
    
    conn = redshift_connector.connect(
        host=host,
        database=database,
        user= username,
        password = password
    )
    return conn


#%%
#function to execute and return the query results

def exquery(query_text: str) ->pd.DataFrame:
    """Actually executes the query text

    Keyword arguments:
    query_text: string of SQL to be executed against Redshift database

    Can be used to exeucte a query without having a file
    """
    
    conn = createconnection()
    
    cursor: redshift_connector.Cursor = conn.cursor()
    cursor.execute(query_text)
    result: pd.DataFrame = cursor.fetch_dataframe()
    
    cursor.close()
    conn.close()
    
    return result

#%%
#Todo: add option to pass parse dates list
def queryredshift(filepath: str):
    """Execute a query and return data
    
    Keyword arguements:
    filepath: a path to sql file that when executed will return one data set
    """
    with open(filepath, 'r') as file:
        query_text = file.read()
        
    #conn = createconnection()
    
    #cursor: redshift_connector.Cursor = conn.cursor()
    #cursor.execute(query_text)
    #result: pd.DataFrame = cursor.fetch_dataframe()
    
    #cursor.close()
    #conn.close()
    
    return exquery(query_text)

#%%
def queryworldwidewithwhere(filepath: str, **kwargs) -> pd.DataFrame:
    """
    
    Conside using the more dynamic querywithwhere function!
    
    Executes a query against World Wide Enrollments with the option for 
    several filters in the where clause. 
    
    Remember to consider the Enrolled Paramater in your Query File.
        
        Parameters:
            filepath (str): Location of a sql file to execute
            
            OPTIONAL:
            session (str) : Specific Session expects 'class_session_cd = {session} ' in query
            term (str) : Specific term  expects 'time_term_year_ld = {term}' in query
            newreturn (str) : Specific term  expects 'stdnt_new_returning_desc = {newreturn}' in query
            campus (str) : Specific term  expects 'stdnt_campus_ld = {campus}' in query
            firstnew (int) : 'first_new_enroll = {firstnew}' in query

        Returns:
            Dataframe of Query results

    """
    with open(filepath, 'r') as file:
        query_text = file.read()
    
    
    #Keyword Replace for Query
    if 'session' in kwargs:
        query_text = query_text.replace('{session}', "'" + kwargs.get("session") + "'")
    
    if 'term' in kwargs:
        query_text = query_text.replace('{term}', "'" + kwargs.get("term") + "'")
    
    if 'newreturn' in kwargs:
        query_text = query_text.replace('{newreturn}', "'" + kwargs.get("newreturn") + "'")
        
    if 'campus' in kwargs:
        query_text = query_text.replace('{campus}', "'" + kwargs.get("campus") + "'")
    
    #integer values do not need aditional quotes in the SQL text
    if 'firstnew' in kwargs:
        query_text = query_text.replace('{firstnew}',  str(kwargs.get("firstnew")))
    
    if 'date' in kwargs:
        query_text = query_text.replace('{date}', "'" +  kwargs.get("date") + "'")
        
        
    #create Connection and return 
    return exquery(query_text)

#%%
def getlistofOLsessionsinterm(term: str):
    """
    A function for returning the OL# sessions that are in term. Useful for those terms that 
    may only have 2 OL sessions or the older ones that had 4. 
    
    Looks specifically for OL# terms not ones that have OLS.
    
    Parameters:
        term: (str): The term you want a list of OL sessions for.
    """
    #Testing out no directory

    #filepath = 'C:/Users/sboyer9/Anaconda3/Lib/site-packages/redshiftquery/GetOLsInTerm.sql'
    
    filepath = get_dir() + '\GetOLsInTerm.sql'
    ol_df =  queryworldwidewithwhere(filepath = filepath, term = term)
    return ol_df['class_session_cd'].tolist()

#%%
def gettermsbetweeninc(startterm: str, endtermdate: str = 'getdate()', includewinter: bool = False, justlist: bool = False):
    """
    A function for getting a list of terms that are between a starting term and 
    an ending term.
    
        
        Parameters:
            startterm (str):The term to start with, it will be included in the list
            
            OPTIONAL:
            endtermdate (str): A date to end with, it will be included in the list
            include winter (bool): If true will return a list including the winter terms
                if it is False only Fall, Spring and Summer terms are returned
            justlist (bool): if true will return just a list with term names otherwise
            will return a 2 column data frame with term names and dates

        Returns:
            Dataframe terms in order with Dates

    """
    if includewinter:
        filepath = get_dir() + '\GetTermsWithWinter.sql'
    else:
        filepath =  get_dir() + '\GetTermsNoWinter.sql'  
    
    if endtermdate == 'getdate()':
        date = datetime.now() + timedelta(days=90)
        endtermdate = date.strftime("%m/%d/%Y")

    #print(endtermdate)
    #get the subsequent terms 
    term_df = queryworldwidewithwhere(filepath = filepath, term = startterm, date = endtermdate) 
    
    if justlist:
        return term_df['time_term_year_ld'].tolist()
    
    return term_df

    
#%%
def querywithwhere(filepath: str, vardict={}):
    """
    Executes a query against Helio's S3 environment with the option for 
    several filters in the where clause. 
    
    Remember to consider the Enrolled Paramater in your Query File.
        
        Parameters:
            filepath (str): Location of a sql file to execute
            
            OPTIONAL:
            vardict (dict) : a dictionary with keys that represent string variables that we wish
                to replace in our SQL file coded with {variable} and string values that represent a
                string that we would like to replace {variable} with. So that in our SQL query 
                {key} becomes 'value'.
                
                
        Returns:
            Dataframe of Query results

    """
    with open(filepath, 'r') as file:
        query_text = file.read()
    
    
    #Keyword Replace for Query
    if vardict:
        for key, value in vardict.items():
            if isinstance(value, str):
                query_text = query_text.replace('{'+ key +'}', "'" + value + "'")
            else:
                query_text = query_text.replace('{'+ key +'}', value)
        
    #create Connection and return 
    return exquery(query_text)