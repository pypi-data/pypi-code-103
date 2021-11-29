from __future__ import print_function
import pickle
import os
import logging

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import MediaFileUpload
import google.auth
from google.cloud import bigquery
from google.cloud import bigquery_storage_v1beta1

import numpy as np
import pandas as pd
from datetime import datetime
from datetime import timedelta
import re
import json
import base64
import email
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
import sys

try:
    from utils.utils import Helper 
except:
    sys.path.append('./web_imports/gsuite_api_service')
    from utils.utils import Helper 

class GSuite():
    scopes = [
        'https://www.googleapis.com/auth/drive',
        'https://www.googleapis.com/auth/drive.file',
        'https://www.googleapis.com/auth/spreadsheets',
        'https://mail.google.com/'
    ]

    def __init__(self, secrets_path='creds/oauth-creds-gsuite-api.json'):
        self.secretsPath = secrets_path

    def connect(self, service='sheets', version='v4', scopes=scopes, 
        pathToCreds=None, pickleName='token'):
        if pathToCreds is None: pathToCreds = self.secretsPath

        creds = None
        if os.path.exists(f'{pickleName}.pickle'):
            with open(f'{pickleName}.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If no (valid) creds, user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(pathToCreds, scopes)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(f'{pickleName}.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        service = build(service, version, credentials=creds)
        return service

    

class GSheets():
    apiDocs = 'https://developers.google.com/sheets/api/reference/rest'
    major_dimension = ['ROWS', 'COLUMNS']
    value_input_option = ['RAW', 'USER_ENTERED']
    value_render_option = ['FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA']
    dateTimeRenderOption = ['SERIAL_NUMBER', 'FORMATTED_STRING']

    test_ssid = '1wZwiJrkR2p_VhSa-KYm-O2i35RXCrd9aVkCm4q8IZs4'
    test_get_range = 'Sheet1!A1:D14'
    test_update_range = 'Sheet1!A20'

    def __init__(self, scopes=None, secretsPath=None):
        self.service = GSuite(secrets_path=secretsPath).connect(scopes=scopes) if scopes else GSuite(secrets_path=secretsPath).connect()

    def testGet(self, ssid=test_ssid, range=test_get_range, 
        valueRenderOption=value_render_option[0]):

        sheets = self.service.spreadsheets()
        result = sheets.values().get(
            spreadsheetId=ssid, range=range, valueRenderOption=valueRenderOption
        ).execute()
        values = result.get('values', [])
        print(values)
        return values

    def testUpdate(self, ssid=test_ssid, range=test_update_range):
        value_input_option = 'RAW'  # TODO: Update placeholder value.

        value_range_body = {
            "range": range,
            "majorDimension": self.major_dimension[0],
            "values": [
                [1234, 34123],
                [1234, 17634, 1234]
            ]
        }

        request = self.service.spreadsheets().values().update(
            spreadsheetId=ssid, range=range, 
            valueInputOption=value_input_option, body=value_range_body
        )
        response = request.execute()
        return response
    
    def get(self, ssid, range, valueRenderOption=value_render_option[0], 
        majorDimension=major_dimension[0]):

        sheets = self.service.spreadsheets()
        result = sheets.values().get(
            spreadsheetId=ssid, 
            range=range, 
            valueRenderOption=valueRenderOption,
            majorDimension=majorDimension
        ).execute()
        values = result.get('values', [])
        return values
    
    def update(self, ssid, _range, valuesDf, 
        majorDimension=major_dimension[0], valueInputOption=value_input_option[0], 
        includeValuesInResponse=False, responseValueRenderOption=value_render_option[0], 
        responseDateTimeRenderOption=dateTimeRenderOption[0], fillnaWithBlank=True):
        
        values = (valuesDf.fillna('') if fillnaWithBlank else valuesDf).values.tolist()
        value_range_body = {
            "range": _range,
            "majorDimension": majorDimension,
            "values": values
        }
        req = self.service.spreadsheets().values().update(
            spreadsheetId = ssid, 
            range = _range, 
            valueInputOption = valueInputOption,
            body = value_range_body,
            includeValuesInResponse = includeValuesInResponse,
            responseValueRenderOption = responseValueRenderOption,
            responseDateTimeRenderOption = responseDateTimeRenderOption
        )
        res = req.execute()
        return res
    
    def clear(self, ssid, _range):
        ''
    
    def batchGet(self, ssid, range, valueRenderOption=value_render_option[0], 
        majorDimension=major_dimension[0]):
        ''
    
    def batchUpdate(self, ssid, _ranges, valuesDf, 
        majorDimension=major_dimension[0], valueInputOption=value_input_option[0], 
        includeValuesInResponse=False, responseValueRenderOption=value_render_option[0], 
        responseDateTimeRenderOption=dateTimeRenderOption[0], fillnaWithBlank=True):
        ''
    
    def batchClear(self, ssid, _ranges):
        ''
    
    def append(self, ssid, _range, valueInputOption=value_input_option[0]):
        ''
    
    def addCellBorders(self, ssid, _range, sheetId, top, bottom, innerHorizontal):
        ''

    def getColumnNumber(self, col):
        first = ord('A')
        col = col.upper()
        c = col[-1]
        num = ord(c) - first + 1
        if len(col) > 1:
            num = num + 26*getColumnNumber(col[:-1])
        return num
    
    def getIndexesFromRange(self, _range):
        s = re.search(r'(?i)([a-z]*)([0-9]*)(:([a-z]*)([0-9]*))?', _range)
        c1 = s.group(1)
        if c1:
            c1 = getColumnNumber(c1)
        c2 = s.group(4)
        if c2:
            c2 = getColumnNumber(c2)
        r1 = s.group(2)
        if not r1:
            r1 = 1
        return c1, r1, c2, s.group(5)
    
    def create(self, title):
        ss = {
            'properties': {
                'title': title
            }
        }
        ss = self.service.spreadsheets().create(
            body = ss, 
            fields = 'spreadsheetId'
        ).execute()
        return ss.get('spreadsheetId')

class GSlides():

    def __init__(self):
        super().__init__()

class GContacts():
    
    def __init__(self):
        super().__init__()

class GMail():
    apiDocs = 'https://developers.google.com/gmail/api/v1/reference'
    labelListVisibilities = ['labelShowIfUnread', 'labelHide', 'labelShow']
    messageListVisibilities = ['hide', 'show']

    def __init__(self, scopes=None, secretsPath=None):
        self.service = GSuite(secrets_path=secretsPath).connect(scopes=scopes, service='gmail', version='v1') \
            if scopes else GSuite(secrets_path=secretsPath).connect(service='gmail', version='v1')
        self.__helper = Helper()
    
    def buildGmailSearchQuery(self, searchTerm, subject=None, label=None, hasAttachment=False):
        searchQuery = searchTerm
        if subject: searchQuery = f'{searchQuery} subject:"{subject}"'
        if label: searchQuery = f'{searchQuery} label:{label}'
        if hasAttachment: searchQuery = f'{searchQuery} has:attachment'

        return searchQuery

    def fetchEmailIds(self, searchTerm, userId='me', subject=None, label=None, hasAttachment=False, maxResults=None, pageToken=None, includeSpamTrash=False):

        query = self.buildGmailSearchQuery(searchTerm, subject=subject, label=label, hasAttachment=hasAttachment)
        response = self.service.users().messages().list(userId=userId, q=query, pageToken=pageToken, includeSpamTrash=includeSpamTrash, maxResults=maxResults).execute()
        messages = list()

        if 'messages' in response:
            messages.extend(response['messages'])
        
        notReachedMaxResults = lambda lm, mr: len(lm) > mr if type(mr) == int else False
        while ('nextPageToken' in response) and (notReachedMaxResults(messages, maxResults)):
            page_token = response['nextPageToken']
            response = self.service.users().messages().list(userId=userId, q=query, pageToken=page_token, includeSpamTrash=includeSpamTrash, maxResults=maxResults).execute()
            messages.extend(response['messages'])

        print(f'Found {len(messages)} messages')
        return messages
    
    def fetchEmails(self, searchTerm, directory, userId='me', subject=None, label=None, hasAttachment=False, maxResults=None, pageToken=None, includeSpamTrash=False, getAttachments=False):
        '''
        directory: path to destination folder
        '''

        emailIds = self.fetchEmailIds(searchTerm, userId=userId, subject=subject, label=label, hasAttachment=hasAttachment, maxResults=maxResults, pageToken=pageToken, includeSpamTrash=includeSpamTrash)

        messages = list()
        for emailId in emailIds:
            msg_raw = self.service.users().messages().get(userId=userId, id=emailId['id'], format='full').execute()
            hasParts = 'parts' in msg_raw['payload'].keys()
            if not hasParts:
                msg_data = msg_raw['payload']['body']['data']
            elif msg_raw['payload']['parts'][0]['mimeType'] == 'text/plain':
                msg_data = msg_raw['payload']['parts'][0]['body']['data']
            elif (msg_raw['payload']['parts'][0]['mimeType'] == 'multipart/alternative') and ('parts' in msg_raw['payload']['parts'][0]):
                msg_data = msg_raw['payload']['parts'][0]['parts'][0]['body']['data']
            else:
                logging.warning(f'Skipped {emailId}')
                continue
            msg_str = base64.urlsafe_b64decode(msg_data.encode('ASCII'))
            mime_msg = email.message_from_string(msg_str) if type(msg_str) == str else email.message_from_bytes(msg_str)
            msg = mime_msg.get_payload()
            headers = pd.DataFrame(msg_raw['payload']['headers'])
            dt = datetime.fromtimestamp(int(msg_raw['internalDate'])/1000)
            message = {
                'message': msg,
                'date': dt,
                'from': re.findall(r'\b[^\s<>]+[@][^\s<>]+\b', headers.value[headers.name == 'From'].iloc[0], re.DOTALL),
                'to': re.findall(r'\b[^\s<>]+[@][^\s<>]+\b', headers.value[headers.name == 'To'].iloc[0], re.DOTALL),
                'subject': headers.value[headers.name == 'Subject'].iloc[0],
                'headers': headers,
                'messageId': emailId['id'],
                'threadId': emailId['threadId'],
                'labelIds': msg_raw['labelIds'],
            }
            if getAttachments and hasParts:
                message['attachments'] = list()
                for part in msg_raw['payload']['parts']:
                    if part['filename']:
                        attachmentId = part['body']['attachmentId']
                        attachment = self.service.users().messages().attachments().get(userId='me', messageId=emailId['id'], id=attachmentId).execute()
                        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
                        filename = os.path.join(directory, f"{emailId['id']}_{part['filename']}")
                        with open(filename, 'wb') as f:
                            f.write(file_data)
                        message['attachments'].extend([filename])
            messages.extend([message])
        return pd.DataFrame(messages)
    
    def sendEmail(self, subject, body, isBodyHtml=False, _file=None, contactList=None, recipients=None, userId='me'):
        if contactList is None and recipients is None:
            raise ValueError('Either contactList or recipients must be provided.')
        if _file is None:
            message = MIMEText(body, 'html' if isBodyHtml else 'plain')
            message['to'] = recipients
            message['from'] = userId
            message['subject'] = subject
            message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
            message = {'raw': message.decode('utf-8')}
            return self.service.users().messages().send(userId=userId, body=message).execute()
        else:
            message = MIMEMultipart()
            message['to'] = recipients
            message['from'] = userId
            message['subject'] = subject
            msg = MIMEText(body, 'html' if isBodyHtml else 'plain')
            message.attach(msg)
            content_type, encoding = mimetypes.guess_type(_file)
            if content_type is None or encoding is not None:
                content_type = 'application/octet-stream'
            main_type, sub_type = content_type.split('/', 1)
            if main_type == 'text':
                with open(_file, 'rb') as f:
                    msg = MIMEText(f.read().decode('utf-8'), _subtype=sub_type)
            elif main_type == 'image':
                with open(_file, 'rb') as f:
                    msg = MIMEImage(f.read(), _subtype=sub_type)
            elif main_type == 'audio':
                with open(_file, 'rb') as f:
                    msg = MIMEAudio(f.read(), _subtype=sub_type)
            else:
                with open(_file, 'rb') as f:
                    msg = MIMEBase(main_type, sub_type)
                    msg.set_payload(f.read())
            filename = os.path.basename(_file)
            msg.add_header('Content-Disposition', 'attachment', filename=filename)
            message.attach(msg)
            message = base64.urlsafe_b64encode(message.as_string().encode("utf-8"))
            message = {'raw': message.decode('utf-8')}
            return self.service.users().messages().send(userId='me', body=message).execute()
    
    def parseLink(self, linkRegex):
        ''
    
    def fetchLabels(self, userId='me'):
        labels = self.service.users().labels().list(userId=userId).execute()
        return pd.DataFrame(labels['labels'])
    
    def createLabel(self, name, userId='me', labelListVisibility=labelListVisibilities[2], messageListVisibility=messageListVisibilities[1], bgColor='#ffffff', textColor='#ffffff'):
        if (not self.__helper.isValidGmailLabelColor(bgColor)) \
            or (not self.__helper.isValidGmailLabelColor(textColor)):
            raise ValueError('Invalid color. Use __helper.possibleGmailLabelColors() to view possible colors.')

        properties = {
            'name': name,
            'labelListVisibility': labelListVisibility,
            'messageListVisibility': messageListVisibility,
            'color': {
                'backgroundColor': bgColor,
                'textColor': textColor
            }
        }

        label = self.service.users().labels().create(userId=userId, body=properties).execute()
        return label['id']
    
    def deleteLabel(self, name=None, label_id=None, userId='me'):
        if label_id:
            try:
                self.service.users().labels().delete(userId=userId, id=label_id).execute()
            except:
                pass
        elif name:
            labels = self.service.users().labels().list(userId=userId).execute()
            if labels and labels['labels']:
                df = pd.DataFrame.from_dict(labels['labels'], orient='columns')
                df = df[df.name == name]
                for i in df.id:
                    self.deleteLabel(label_id=i)

class GDrive():
    apiDocs = 'https://developers.google.com/drive/api/v3/reference'

    def __init__(self, scopes=None, secretsPath=None):
        self.service = GSuite(secrets_path=secretsPath).connect(service='drive', version='v3', scopes=scopes) \
            if scopes else GSuite(secrets_path=secretsPath).connect(service='drive', version='v3')

    def moveFile(self, id, newFolderId):
        file = self.service.files().get(fileId = id, fields = 'parents').execute()
        current_parents = ','.join(file.get('parents'))
        file = self.service.files().update(
            fileId = id,
            addParents = newFolderId,
            removeParents = current_parents,
            fields = 'id, parents'
        ).execute()
    
    def uploadFile(self, pathToFile, name, folderIds, mimetype, resumable=True):
        file_metadata = {
            'name': name,
            'parents': folderIds
        }
        media = MediaFileUpload(
            pathToFile,
            mimetype=mimetype,
            resumable=resumable
        )
        file = self.service.files().create(
            body = file_metadata,
            media_body = media,
            fields = 'id'
        ).execute()
        return file.get('id')

class BigQuery():
    apiDocs = [
        'https://googleapis.dev/python/bigquery/latest/usage/index.html',
        'https://cloud.google.com/bigquery/docs/pandas-gbq-migration',
        'https://cloud.google.com/bigquery/docs/tables',
        'https://cloud.google.com/bigquery/docs/reference/libraries',
        'https://cloud.google.com/bigquery/docs/interacting-with-bigquery'
    ]
    write_disposition = ['WRITE_EMPTY', 'WRITE_TRUNCATE', 'WRITE_APPEND']

    def __init__(self, requireBQStorage=False, secrets_path='creds/gcloud-api-data-science-274806.json'):
        secretsPath = secrets_path
        if requireBQStorage:
            credentials, project_id = google.auth.load_credentials_from_file(
                secretsPath, 
                scopes=["https://www.googleapis.com/auth/cloud-platform"])
            self.client = bigquery.Client(credentials=credentials, project=project_id)
            self.bqstorage_client = bigquery_storage_v1beta1.BigQueryStorageClient(credentials=credentials)
        else:
            self.client = bigquery.Client.from_service_account_json(secretsPath)
            self.bqstorage_client = None
    
    def loadTable(self, df, table_id, schema, write_disposition=write_disposition[0], wait=True):
        '''
        schema-example: [
            bigquery.SchemaField("full_name", "INT64", mode="REQUIRED"),
            bigquery.SchemaField("age", "INT64")
        ]
        '''

        job_config = bigquery.LoadJobConfig(schema=schema)
        job_config.write_disposition = write_disposition
        job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
        if wait:
            job.result()
        return job.job_id, job
    
    def createTable(self, table_id, schema):
        table = bigquery.Table(table_id, schema=schema)
        table = self.client.create_table(table)
        return table

    def query(self, sql, project_id=None, job_config=None, destination=None):
        query_parameters = list()
        if job_config:
            for param in job_config:
                query_parameters.append(bigquery.ScalarQueryParameter(
                    param['parameter'], param['dataType'], param['value']
                ))
        query_config = bigquery.QueryJobConfig(query_parameters=query_parameters, destination=destination)
        job_config = query_config

        return self.client.query(sql, project=project_id, job_config=job_config).to_dataframe(bqstorage_client=self.bqstorage_client)
    
    def getTableProperties(self, table_id):
        t = self.client.get_table(table_id)
        return {
            'project': t.project,
            'datasetId': t.dataset_id,
            'tableId': t.table_id,
            'sizeBytes': t.num_bytes,
            'rows': t.num_rows,
            'created': t.created,
            'lastModified': t.modified,
            'expires': t.expires,
            'schema': t.schema,
            'labels': t.labels,
            'path': t.path,
            'ragePartitioning': t.range_partitioning,
            'reference': t.reference,
            'link': t.self_link,
            'streamingBuffer': t.streaming_buffer,
            'viewQuery': t.view_query,
            'table': t
        }
    
    def deleteTable(self, table_id):
        self.client.delete_table(table_id)
    
    def copyTable(self, table_id, destination_table_id):
        self.client.copy_table(table_id, destination_table_id)
    
    def deleteDataset(self, datasetId):
        self.client.delete_dataset(datasetId)
    
    def createDataset(self, datasetId):
        self.client.create_dataset(datasetId)
    
    def getDatasetTables(self, datasetId):
        tableIterator = self.client.list_tables(datasetId)
        tables = []
        for t in tableIterator:
            tables.append([f'{t.project}.{t.dataset_id}.{t.table_id}', t])
        return tables

if __name__ == '__main__':
    print('Run get/update tests')
    gsuite = GSuite()
    service = gsuite.connect()
    gs = GSheets()
    gs.testGet(service)
    gs.testUpdate(service)
    vals = gs.get(service, '1d43MekUMTd0Aa-95QDiwTkcz28FQ-0J8EFuungOxuCg', 'A1:D30', valueRenderOption=gs.valueRenderOption[1])
    print(vals)
