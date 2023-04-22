import sqlite3
import os

class DB:

	def __init__(self):

		self.path = "C:\\Users\\i.yurasov\\Desktop\\dev\\gs-bimcloud-automate\\stats.db"
		self.con = None

		self.connect();

	def connect(self):
		try:
			con = sqlite3.connect(self.path)
			con.execute('CREATE TABLE IF NOT EXISTS folders (id text, pid text, name text, logtime integer)')
			con.execute('CREATE TABLE IF NOT EXISTS files (id text, pid text, name text, type text, size integer, modified integer, build text, logtime integer)')
			self.con = con
		except:
			print('something wrong with connect')

	def table(self, name):
		try:
			c = self.con.cursor()
			c.execute('SELECT * FROM ' + name)
			return(c.fetchall())
		except:
			print('something wrong with table')


	def addFolderData(self, id, pid, name, logtime):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO folders (id, pid, name, logtime) VALUES (?, ?, ?, ?)", (id, pid, name, logtime))
			self.con.commit()
		except:
			print('something wrong with folder insertion')

	def addFileDataData(self, id, pid, name, type, size, modified, build, logtime):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO files (id, pid, name, type, size, modified, build, logtime) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (id, pid, name, type, size, modified, build, logtime))
			self.con.commit()
		except:
			print('something wrong with file insertion')