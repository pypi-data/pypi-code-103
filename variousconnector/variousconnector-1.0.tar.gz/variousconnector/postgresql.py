# -*- coding: utf-8 -*-
"""
Created on Mon Aug  2 16:14:58 2021

@author: WEIHAO
"""

from sshtunnel import SSHTunnelForwarder
from sqlalchemy import create_engine
import pandas as pd

class postgresql_connector:
    def __init__(self, credential):
        try:
            self.pgres_host = credential['host']
            self.pgres_port = credential['port']
            self.psql_user = credential['user']
            self.psql_pass = credential['pwd']
    
            if credential['ssh_enable'] is True:
                self.ssh_host = credential['ssh_host']
                self.ssh_user = credential['ssh_user']
                self.ssh_password = credential['ssh_pwd']
        except:
            credential_example = {'host':'....us-west-2.rds.amazonaws.com',
                                  'port':'5432',
                                  'user':'pg user_name',
                                  'pwd':'pg password',
                                  'ssh_enable':'True/False',
                                  'ssh_host':'ssh host (not require if ssh_enable is False)',
                                  'ssh_user':'ssh user name (not require if ssh_enable is False)',
                                  'ssh_pwd':'ssh pwd (not require if ssh_enable is False)'
                                  }
            raise ValueError(f"credential format is incorrect \n"
                             f"here is an example: \n"
                             f"{credential_example}"
                             )
            
        self.server = SSHTunnelForwarder(
            (self.ssh_host, 22),
            ssh_username=self.ssh_user,
            ssh_password=self.ssh_password,
            remote_bind_address=(self.pgres_host, self.pgres_port),
            )
        server = self.server
        server.start()  # start ssh server
        self.local_port = server.local_bind_port
        print(f'Server connected via SSH || Local Port: {self.local_port}...')

    def query(self, db, query):
        psql_user = self.psql_user
        psql_pass = self.psql_pass
        engine = create_engine(f'postgresql://{psql_user}:{psql_pass}@127.0.0.1:{self.local_port}/{db}')
        print(f'Database [{db}] session created...')
        self.query_df = pd.read_sql(query, engine)
        print('<> Query Sucessful <>')
        engine.dispose()
        return self.query_df
