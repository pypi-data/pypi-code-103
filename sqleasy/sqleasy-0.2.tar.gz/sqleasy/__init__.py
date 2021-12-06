import sqlite3
import os

def connect(name):
	sqlite3.connect(name+".db")

def close(name):
	db = sqlite3.connect(name+".db")
	db.close()

def createTable(database, table, args):
	db = sqlite3.connect(database+".db")
	cursor = db.cursor()
	cursor.execute("CREATE TABLE IF NOT EXISTS "+table+" ("+args+");")
	db.close()

def insertValue(database, table, arg1, arg2):
	db = sqlite3.connect(database+".db")
	cursor = db.cursor()
	cursor.execute("INSERT INTO " + table + " ("+arg1+") VALUES ("+arg2+")")
	db.commit()
	db.close()

def getValue(database, arg1, table):
	db = sqlite3.connect(database+".db")
	cursor = db.cursor()
	cursor.execute("SELECT " +arg1+ " FROM " + table + ";")
	for linha in cursor.fetchall():
		print(linha)
	db.close()

def changeValue(database, table, arg1, value1, arg2, value2):
	db = sqlite3.connect(database+".db")
	cursor = db.cursor()
	cursor.execute(f"UPDATE {table} SET {arg1}={value1} WHERE {arg2}={value2}")
	db.commit()
	db.close()

def deleteValue(database, table, arg1, value1):
	db = sqlite3.connect(database+".db")
	cursor = db.cursor()
	cursor.execute(f"DELETE FROM {table} WHERE {arg1}={value1}")
	db.commit()
	db.close()

def addColumnInTable(database, table, column, arg1):
	db = sqlite3.connect(database+".db")
	cursor = db.cursor()
	cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {arg1};")
	db.commit()
	db.close()

def deleteTable(database, table):
	db = sqlite3.connect(database+".db")
	cursor = db.cursor()
	cursor.execute(f"DROP TABLE {table};")
	db.commit()
	db.close()