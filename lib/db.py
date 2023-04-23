import sqlite3
import os
import time

class DB:

	def __init__(self):

		self.path = "C:\\Users\\i.yurasov\\Desktop\\dev\\gs-bimcloud-automate\\stats.db"
		self.con = None
		self.logId = 0
		self.logTime = 0
		
		self.connect();
		self.logPrep();

	def connect(self):
		try:
			con = sqlite3.connect(self.path)
			con.execute(
				'CREATE TABLE IF NOT EXISTS folders \
				(id text, pid text, name text, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS files \
				(id text, pid text, name text, type int, size real, lock bool, modified integer, build text, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS users \
				(id text, login text, name text, jfid text, online bool, spotted integer, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS entries \
				(id integer primary key, logtime integer)'
			)
			self.con = con
		except:
			print('something wrong with connect')


	def logPrep(self):
		try:
			self.logTime = int(time.time())
			c = self.con.cursor()
			c.execute('SELECT MAX(id) FROM entries')
			logId = c.fetchone()[0]
			if logId is not None: self.logId = logId + 1
		except:
			print('something wrong while retrieving the log id')

	def logEntry(self):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO entries (id, logtime) VALUES (?, ?)", (self.logId, self.logTime))
			self.con.commit()
		except:
			print('something wrong with entry logging')

	def addFolderData(self, id, pid, name):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO folders (id, pid, name, log) VALUES (?, ?, ?, ?)", (id, pid, name, self.logId))
			self.con.commit()
		except:
			print('something wrong with folder insertion')

	def addFileDataData(self, id, pid, name, type, size, lock, modified, build):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO files (id, pid, name, type, size, lock, modified, build, log) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, pid, name, type, size, lock, modified, build, self.logId))
			self.con.commit()
		except:
			print('something wrong with file insertion')

	def addUserData(self, id, login, name, jfid, online, spotted):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO users (id, login, name, jfid, online, spotted, log) VALUES (?, ?, ?, ?, ?, ?, ?)", (id, login, name, jfid, online, spotted, self.logId))
			self.con.commit()
		except:
			print('something wrong with user insertion')