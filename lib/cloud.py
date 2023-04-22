import random
import string
import itertools
import os
import requests
import time
import json
from .db import DB
from .managerapi import ManagerApi
from .blobserverapi import BlobServerApi
from .url import join_url, parse_url
from .errors import BIMcloudBlobServerError, BIMcloudManagerError

CHARS = list(itertools.chain(string.ascii_lowercase, string.digits))
PROJECT_ROOT = 'Project Root'
PROJECT_ROOT_ID = 'projectRoot'
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

		self._root_dir_name = Cloud.to_unique('DEMO_RootDir')
		self._sub_dir_name = Cloud.to_unique('DEMO_SubDir')
		self._root_dir_data = None
		self._sub_dir_data = None
		self._inner_dir_path = None
		self._model_server_urls = {}
		self._blob_server_sessions = {}

		# Changeset polling starts on revision 0
		self._next_revision_for_sync = 0

		self.logtime = int(time.time())

	def run(self):
		try:
			self.login()
			self.fetchFolders()
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

	def fetchFolders(self, pid=PROJECT_ROOT_ID):
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
				if f['type'] == 'library':
					build = '0'
				else:
					build = f['$version']
				self.db.addFileDataData(f['id'], f['$parentId'], f['name'], f['type'], f['$size'], f['$modifiedDate'], build, self.logtime)
				print(f["name"])
				if f['type'] == 'library':
					pass
				else:
					self.fetchUsers(f['$joinedUsers'], f['id'], f['$parentId'])
		except BIMcloudManagerError as err:
			print(f'[{round((time.time() - TS),10)}]: {err}')		

	def fetchUsers(self, users, jfid, jpid):
		try:
			for u in users:
				self.db.addUserData(u['id'], u['username'], u['name'], jfid, jpid, u['online'], u['lastActive'], self.logtime)
				print(u['username'])
		except:
			print(f'[{round((time.time() - TS),10)}]: wrong user data')


	@staticmethod
	def to_unique(name):
		return f'{name}_{random.choice(CHARS)}{random.choice(CHARS)}{random.choice(CHARS)}{random.choice(CHARS)}'


	#$size