import sqlite3
import os
import time

class DB:

	def __init__(self, lid=0, logtime=0):

		self.path = os.path.dirname(__file__).split("lib")[0] + 'stats.db'
		self.con = None
		self.lid = lid
		self.logtime = logtime

		self.connect();

	def connect(self):
		try:
			con = sqlite3.connect(self.path)
			con.execute(
				'CREATE TABLE IF NOT EXISTS entries \
				(id integer primary key, logtime integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS folders \
				(id text, pid text, sid text, name text, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS files \
				(id text, pid text, sid text, name text, type text, size real, lock bool, modified integer, build text, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS users \
				(id text, sid text, login text, name text)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS users_files \
				(id text, jfid text, online bool, activity integer, log integer)'
			)
			con.execute(
				'CREATE TABLE IF NOT EXISTS servers \
				(id text, name text, freespace real, firstRun integer, lastStart integer, log integer)'
			)
			self.con = con
		except:
			print('something wrong with connect')


	def logEntry(self, logtime=0):
		if logtime == 0: logtime = self.logtime
		try:
			c = self.con.cursor()
			c.execute("SELECT id, logtime FROM entries WHERE logtime = ?", (logtime,))
			row = c.fetchone()
			if row is None:
				c.execute('SELECT MAX(id) FROM entries')
				lid = c.fetchone()
				if lid[0] is not None:
					self.lid = lid[0]+1
				# add new log entry
				try:
					c.execute("INSERT INTO entries (id, logtime) VALUES (?, ?)", (self.lid, logtime))
					self.con.commit()
				except:
					print('something wrong with entry logging')
			else:
				self.lid = row[0]
		except:
			print('something wrong while retrieving the log id')

	def addFolderData(self, id, pid, sid, name):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO folders (id, pid, sid, name, log) VALUES (?, ?, ?, ?, ?)", (id, pid, sid, name, self.lid))
			self.con.commit()
		except:
			print('something wrong with folder insertion')

	def addFileData(self, id, pid, sid, name, type, size, lock, modified, build):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO files (id, pid, sid, name, type, size, lock, modified, build, log) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (id, pid, sid, name, type, size, lock, modified, build, self.lid))
			self.con.commit()
		except:
			print('something wrong with file insertion')

	def addUserData(self, id, login, name, jfid, sid, online, activity):
		try:
			c = self.con.cursor()
			c.execute("SELECT id, sid FROM users WHERE id = ? AND sid = ?", (id, sid,))
			fetch = c.fetchone()
			if fetch is None:
				c.execute("INSERT INTO users (id, sid, login, name) VALUES (?, ?, ?, ?)", (id, sid, login, name))
			# file joins
			c.execute("INSERT INTO users_files (id, jfid, online, activity, log) VALUES (?, ?, ?, ?, ?)", (id, jfid, online, activity, self.lid))
			self.con.commit()
		except:
			print('something wrong with user insertion')

	def addServerData(self, id, name, freespace, firstRun, lastStart):
		try:
			c = self.con.cursor()
			c.execute("INSERT INTO servers (id, name, freespace, firstRun, lastStart, log) VALUES (?, ?, ?, ?, ?, ?)", (id, name, freespace, firstRun, lastStart, self.lid))
			self.con.commit()
		except:
			print('something wrong with server insertion')

	def close(self):
		self.con.cursor().close()
		self.con.close()