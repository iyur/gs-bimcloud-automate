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
				'CREATE TABLE IF NOT EXISTS entries \
				(id integer primary key, logtime integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS folders \
				(id text, pid text, name text, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS files \
				(id text, pid text, sid text, name text, type int, size real, lock bool, modified integer, build text, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS users \
				(id text, login text, name text, online bool, spotted integer, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS users_files \
				(id text, jfid text, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS servers \
				(id text, name text, freespace integer, firstRun integer, lastStart integer, log integer)'
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

	def addFileData(self, id, pid, sid, name, type, size, lock, modified, build):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO files (id, pid, sid, name, type, size, lock, modified, build, log) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, pid, sid, name, type, size, lock, modified, build, self.logId))
			self.con.commit()
		except:
			print('something wrong with file insertion')

	def addUserData(self, id, login, name, jfid, online, spotted):
		try:
			c = self.con.cursor()
			c.execute("SELECT id FROM users WHERE id = ?", (id,))
			fetch = c.fetchone()
			if fetch is None:
				c.execute("INSERT INTO users (id, login, name, online, spotted, log) VALUES (?, ?, ?, ?, ?, ?)", (id, login, name, online, spotted, self.logId))
			c.execute("INSERT INTO users_files (id, jfid, log) VALUES (?, ?, ?)", (id, jfid, self.logId)) # files relationship
			self.con.commit()
		except:
			print('something wrong with user insertion')

	def addServerData(self, id, name, freespace, firstRun, lastStart):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO servers (id, name, freespace, firstRun, lastStart, log) VALUES (?, ?, ?, ?, ?, ?)", (id, name, freespace, firstRun, lastStart, self.logId))
			self.con.commit()
		except:
			print('something wrong with server insertion')