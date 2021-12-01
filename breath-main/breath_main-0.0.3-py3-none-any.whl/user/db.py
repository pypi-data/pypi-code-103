import sqlite3 
import hashlib

def make_hashes(password):
		return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
	if make_hashes(password) == hashed_text:
		return hashed_text
	return False 

#Referência: https://blog.jcharistech.com/2020/05/30/how-to-add-a-login-section-to-streamlit-blog-app/

class BD:

	def __init__(self, conn):
		self.conn = conn
		self.c = conn.cursor()

		self.create_usertable()

	def create_usertable(self):
		self.c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')

	def add_userdata(self, username,password):
		self.c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
		self.conn.commit()

	def login_user(self, username,password):
		self.c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
		data = self.c.fetchall()
		return data

	def view_all_users(self):
		self.c.execute('SELECT * FROM userstable')
		data = self.c.fetchall()
		return data

	def delete_all_users(self):
		self.c.execute('DELETE * FROM userstable')


	