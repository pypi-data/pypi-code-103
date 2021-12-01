
import pandas as pd 

import numpy as np
import matplotlib.pyplot as plt
import boto3
import numpy as np
import logging
import zipfile

# Logging
logger = logging.getLogger(__name__)

generic_usernames=[
    'accounting', 'accountmanagement', 'accountmanagers', 'accounts', 'accountspayable', 'accountsreceivable',
    'admin', 'administrator', 'admissions', 'advising', 'afterhours', 'alert', 'ar', 'aula', 'benefits', 'billing',
    'bookings', 'careers', 'casl.unsubscribe', 'claims', 'client_services', 'clientcare', 'clientrelations',
    'clientservices', 'clientsupport', 'communications', 'compliance', 'concierge', 'connect',
    'contact', 'contracts', 'corporate', 'cqcpsupport', 'crmsupport', 'croweunsubscribe', 'cs', 'csm',
    'customer.service', 'customer.support', 'customercare', 'customerrelations', 'customersatisfaction',
    'customerservice', 'customersuccess', 'customersupport', 'custserv', 'dataprivacy', 'dataprotection', 'design',
    'digital', 'disclaimer', 'dispatch', 'dnerequests', 'edisupport', 'education', 'enquiries', 'events', 'facilities',
    'feedback', 'finance', 'fundraising', 'getinvolved', 'hello', 'help', 'helpdesk', 'hr', 'hr.uk', 'hrteam',
    'humanresources', 'idmssupport', 'implementation', 'info', 'information', 'infosec', 'insidesales', 'inventory',
    'inventorysupport', 'invoices', 'it', 'ithelp', 'ithelpdesk', 'itservicedesk', 'itsupport', 'jobs', 'legal',
    'legalcompliance', 'licensing', 'logistics', 'mail', 'mailadm', 'maintenance', 'marketing', 'marketingteam',
    'media', 'membership', 'no-more-mail', 'noc', 'northsales', 'office', 'onboarding', 'operations', 'ops', 'opt-out',
    'orders', 'partners', 'partnersupport', 'parts', 'payables', 'payroll', 'people', 'peopleops', 'planning', 'pm',
    'pmo', 'postmaster', 'privacy', 'procurement', 'product', 'production', 'projectmanagement', 'projects',
    'purchasing', 'quotes', 'r&d', 'reception', 'recruiting', 'recruitment', 'request', 'reservations', 'returns',
    'sales', 'salessupport', 'samples', 'scheduling', 'security', 'service', 'servicedesk', 'services', 'shipping',
    'solutions', 'status', 'success', 'support', 'support.us', 'sysadmin', 'talent', 'team', 'technical',
    'technicalservice', 'techsupport', 'ticketsales', 'traffic', 'training', 'uk', 'underwriting', 'unsubscribe',
    'websitesupport']

non_corp_emails=pd.read_csv('EmailPublicDomains.csv')['Domain'].tolist()

non_corp_emails_string='|'.join(non_corp_emails)
generic_emails_string='|'.join(generic_usernames)

def read_first_lines_of_csv(path,N):
    with open(path) as myfile:
        head = [next(myfile) for x in range(N)]
    print(head)
    return 1


def extract_zip(zippath,extraction_path):
    with zipfile.ZipFile(zippath, 'r') as zip_ref:
        zip_ref.extractall(extraction_path)
    return 1


def clean_null_and_personal_emails(df):
    print(df.shape)
    df=df[~(df['email'].isna())]  # filtrar emails vacios
    df['email']=df['email'].str.lower() # pasar a minusculas 
    df.drop_duplicates(subset='email',keep='last',inplace=True)  # dropear mails duplicados, me quedo siempre con el ultimo
    df=df[~(df['email']=='null')] # eliminar registros con email=null
    df=df[~(df['email']=='')] # eliminar registrion con email = ''
    df=df[~(df['email'].str.contains('linkedin'))] # eliminar registros que contengan linkedin
    df=df[~(df['email'].str.contains('\t'))]   #  elinminar registros que contengan tabulaciones
    df=df[(df['email'].str.contains('@'))]  # exijo que tenga un @ 
    df=df[~(df['email'].str.contains(non_corp_emails_string))] #  me quedo con correos corporation
    df=df[~(df['email'].str.contains(generic_emails_string))] # me quedo con emails no genericos
    print(df.shape)
    return df

def rearrange_columns(df):
    print(df.columns)
    col_list = []
    if 'email' not in df:
        df['email'] = np.nan
    if 'linkedin' not in df:
        df['linkedin'] = np.nan 
    if 'first_name' not in df:
        df['first_name']=np.nan
    if 'last_name' not in df:
        df['last_name']=np.nan
    if 'full_name' not in df:
        df['full_name']=np.nan
    if 'phone' not in df:
        df['phone']=np.nan
        
    
    col_list.append('email')
    col_list.append('first_name') 
    col_list.append('last_name')  
    col_list.append('full_name')
    col_list.append('linkedin')
    col_list.append('phone')
    df=df[col_list]
    print('changed columns')
    return df


def save_to_s3(df,bucket,prefix,output_filename):
    df.to_csv(output_filename,index=False,compression="gzip",quoting=csv.QUOTE_ALL)
    boto3.Session().resource('s3').Bucket(bucket).Object(os.path.join(prefix, output_filename)).upload_file(output_filename)
    return 0