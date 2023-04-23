import random
import os
import requests
import time
import json
from datetime import datetime
from .db import DB
from .managerapi import ManagerApi
from .blobserverapi import BlobServerApi
from .url import join_url, parse_url
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

		self._model_server_urls = {}
		self._blob_server_sessions = {}
		self._next_revision_for_sync = 0

		self.logtime = int(time.time())

	def run(self):
		try:
			self.login()
			self.fetchFolders()
			# file = self._manager_api.get_resource(self._session_id, by_id='99A77C87-0EBC-460F-BB7D-779D454F0B98')
			# print(file)
			# print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
			# print(datetime.fromtimestamp(int(time.time())))
		finally:
			self.logout()

	def login(self):
		print(f'[{round((time.time() - TS),10)}]: Try to login as {self.username} ...')
		self._user_id, self._session_id = self._manager_api.create_session(self.username, self._password, self.client_id)
		print(f'[{round((time.time() - TS),10)}]: Logged in successfully')


	def logout(self):
		self._manager_api.close_session(self._session_id)
		for server_id in self._blob_server_sessions:
			session_id, api = self._blob_server_sessions[server_id]
			api.close_session(session_id)
		self._blob_server_sessions = {}
		self._session_id = None
		self._model_server_urls = {}
		print(f'[{round((time.time() - TS),10)}]: Logged out')

	def count(self, pid):
		c = 0
		try:
			data = self._manager_api.get_resource(self._session_id, by_id=pid)
			for d in data['members']:
				c += 1
				folder = self._manager_api.get_resource(self._session_id, by_id=d)
				for f in folder['members']:
					c += 1
			print(f'[{round((time.time() - TS),10)}]: Total items - {c} found')
			return(c)
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')

	def fetchFolders(self, pid='projectRoot'):
		try:
			options = { 'sort-by': 'name' }
			criterion = { '$eq': { '$parentId': pid } }
			folders = self._manager_api.get_resources_by_criterion(self._session_id, criterion, options)
			for f in folders:
				self.db.addFolderData(f['id'], f['$parentId'], f['name'], self.logtime)
				self.fetchFiles(f['id'])
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')

	def fetchFiles(self, pid):
		try:
			options = { 'sort-by': 'name' }
			criterion = { '$eq': { '$parentId': pid } }
			files = self._manager_api.get_resources_by_criterion(self._session_id, criterion, options)
			for f in files:
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
				self.db.addFileDataData(f['id'], f['$parentId'], f['name'], type, f['$size'], lock, f['$modifiedDate']/1000, build, self.logtime)
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')		

	def fetchUsers(self, users, jfid):
		try:
			for u in users:
				self.db.addUserData(u['id'], u['username'], u['name'], jfid, u['online'], round(u['lastActive']/1000,0), self.logtime)
		except:
			print(f'[{round((time.time() - TS),10)}]: wrong user data')