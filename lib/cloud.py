import time
from .db import DB
from .managerapi import ManagerApi
from .errors import BIMcloudBlobServerError, BIMcloudManagerError

TS = time.time()

class Cloud:
	def __init__(self, url, user, pwd, cid, lid):
		self.url = url
		self.username = user
		self.password = pwd
		self.client = cid
		self.sessionId = None
		self.userId = None

		self.apiBCM = ManagerApi(url)
		self.apiDB = DB(lid=lid)
		self.serverId = ''

		self.iFolders = 0
		self.iFiles = 0
		self.iUsers = 0
		self.iServers = 0

	def collect(self):
		try:
			self.login()
			self.fetchServers()
			self.fetchFolders()
			print(f'[{round((time.time() - TS),10)}]: Added to #{self.apiDB.lid}: {self.iServers} servers, {self.iFolders} folders, {self.iFiles} files and {self.iUsers} joins ({self.url})')
		finally:
			self.logout()

	def login(self):
		self.userId, self.sessionId = self.apiBCM.create_session(self.username, self.password, self.client)
		print(f'[{round((time.time() - TS),10)}]: Logged as {self.username}')


	def logout(self):
		self.apiDB.close()
		self.apiBCM.close_session(self.sessionId)
		self.sessionId = None
		print(f'[{round((time.time() - TS),10)}]: Logged out')

	def fetchServers(self):
		options = { 'sort-by': 'name' }
		criterion = { '$eq': { 'type': 'modelServer' } }
		try:
			portal = self.apiBCM.get_resource(self.sessionId, by_id='portalServer')
			modules = self.apiBCM.get_resources_by_criterion(self.sessionId, criterion, options)
			for m in modules:
				self.iServers += 1
				self.serverId = m['id'] # TODO: fix this
				self.apiDB.addServerData(m['id'], m['name'], m['$projectFreeSpace'], round(portal['firstRunningTime']/1,0), round(portal['$lastStartOn']/1,0))
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')


	def fetchFolders(self, pid='projectRoot'):
		print(f'[{round((time.time() - TS),10)}]: Retrieving resources ...')
		options = { 'sort-by': 'name' }
		criterion = { '$eq': { '$parentId': pid } }
		try:
			folders = self.apiBCM.get_resources_by_criterion(self.sessionId, criterion, options)
			for f in folders:
				self.iFolders += 1
				self.apiDB.addFolderData(f['id'], f['$parentId'], self.serverId, f['name'])
				self.fetchFiles(f['id'])
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')

	def fetchFiles(self, pid):
		options = { 'sort-by': 'name' }
		criterion = { '$eq': { '$parentId': pid } }
		try:
			files = self.apiBCM.get_resources_by_criterion(self.sessionId, criterion, options)
			for f in files:
				self.iFiles += 1
				lock = False
				if f['type'] == 'library':
					build = 'n/a'
				else:
					build = f['$version']
					if f['access'] == 'locked':
						lock = True
					self.fetchUsers(f['$joinedUsers'], f['id'], f['modelServerId'])
				self.apiDB.addFileData(f['id'], f['$parentId'], f['modelServerId'], f['name'], f['type'], f['$size'], lock, f['$modifiedDate']/1000, build)
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')		

	def fetchUsers(self, users, jfid, sid):
		try:
			for u in users:
				self.iUsers += 1
				self.apiDB.addUserData(u['id'], u['username'], u['name'], jfid, sid, u['online'], round(u['lastActive']/1000,0))
		except:
			print(f'[{round((time.time() - TS),10)}]: wrong user data')