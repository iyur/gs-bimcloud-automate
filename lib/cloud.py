import time
from .db import DB
from .managerapi import ManagerApi
from .errors import BIMcloudBlobServerError, BIMcloudManagerError

TS = time.time()

class Cloud:
	def __init__(self, manager_url, username, password, client_id):
		self._manager_api = ManagerApi(manager_url)
		self.db = DB()

		self.username = username
		self._password = password
		self.client_id = client_id
		self._session_id = None
		self._user_id = None

		self._blob_server_sessions = {}
		self._next_revision_for_sync = 0

		self.iFolders = 0
		self.iFiles = 0
		self.iUsers = 0
		self.iServers = 0

	def run(self):
		try:
			self.login()
			self.db.logEntry()
			self.fetchFolders()
			self.fetchServers()
			print(f'[{round((time.time() - TS),10)}]: Entry #{self.db.logId}: {self.iServers} servers, {self.iFolders} folders, {self.iFiles} files and {self.iUsers} joins')
		finally:
			self.logout()

	def login(self):
		self._user_id, self._session_id = self._manager_api.create_session(self.username, self._password, self.client_id)
		print(f'[{round((time.time() - TS),10)}]: Logged as {self.username}')


	def logout(self):
		self._manager_api.close_session(self._session_id)
		for server_id in self._blob_server_sessions:
			session_id, api = self._blob_server_sessions[server_id]
			api.close_session(session_id)
		self._blob_server_sessions = {}
		self._session_id = None
		print(f'[{round((time.time() - TS),10)}]: Logged out')

	def fetchFolders(self, pid='projectRoot'):
		print(f'[{round((time.time() - TS),10)}]: Retrieving resources ...')
		options = { 'sort-by': 'name' }
		criterion = { '$eq': { '$parentId': pid } }
		try:
			folders = self._manager_api.get_resources_by_criterion(self._session_id, criterion, options)
			for f in folders:
				self.iFolders += 1
				self.db.addFolderData(f['id'], f['$parentId'], f['name'])
				self.fetchFiles(f['id'])
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')

	def fetchFiles(self, pid):
		options = { 'sort-by': 'name' }
		criterion = { '$eq': { '$parentId': pid } }
		try:
			files = self._manager_api.get_resources_by_criterion(self._session_id, criterion, options)
			for f in files:
				self.iFiles += 1
				lock = False
				type = 10
				if f['type'] == 'library':
					build = '0'
					type = 20
				else:
					build = f['$version']
					if f['access'] == 'locked':
						lock = True
					self.fetchUsers(f['$joinedUsers'], f['id'])
				self.db.addFileData(f['id'], f['$parentId'], f['name'], type, f['$size'], lock, f['$modifiedDate']/1000, build)
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')		

	def fetchUsers(self, users, jfid):
		try:
			for u in users:
				self.iUsers += 1
				self.db.addUserData(u['id'], u['username'], u['name'], jfid, u['online'], round(u['lastActive']/1000,0))
		except:
			print(f'[{round((time.time() - TS),10)}]: wrong user data')

	def fetchServers(self):
		options = { 'sort-by': 'name' }
		criterion = { '$eq': { 'type': 'modelServer' } }
		try:
			portal = self._manager_api.get_resource(self._session_id, by_id='portalServer')
			modules = self._manager_api.get_resources_by_criterion(self._session_id, criterion, options)
			for m in modules:
				self.iServers += 1
				self.db.addServerData(m['id'], m['name'], m['$projectFreeSpace'], round(portal['firstRunningTime']/1000,0), round(portal['$lastStartOn']/1000,0))
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')	