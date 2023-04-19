import random
import string
import itertools
import os
import requests
import time
import json
from .managerapi import ManagerApi
from .blobserverapi import BlobServerApi
from .url import join_url, parse_url
from .errors import BIMcloudBlobServerError, BIMcloudManagerError

CHARS = list(itertools.chain(string.ascii_lowercase, string.digits))
PROJECT_ROOT = 'Project Root'
PROJECT_ROOT_ID = 'projectRoot'

class Cloud:
	def __init__(self, manager_url, username, password, client_id):
		self._manager_api = ManagerApi(manager_url)

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

	def run(self):
		# Cloud BEGIN
		self.login()
		try:
			self.get_all_dirs()
			# self.create_dirs()
			# self.upload_files()
			# self.rename_file()
			# self.move_file()
			# self.locate_download_and_delete_files()
			# self.create_directory_tree_and_delete_recursively()
		finally:
			self.logout()
		# Cloud END

	def login(self):
		print(f'Login as {self.username} ...')
		self._user_id, self._session_id = self._manager_api.create_session(self.username, self._password, self.client_id)
		print('Logged in.')


	def get_all_dirs(self):
		# print(self._root_dir_name)
		# folder = self._manager_api.get_resource(self._session_id, by_id=PROJECT_ROOT_ID)
		# obj = self._manager_api.get_resource(self._session_id, by_id="1400432b-2025-4139-9400-959469848bac")
		criterion = { '$eq': { '$parentId': "portalServer" } }
		obj = self._manager_api.get_resource(self._session_id, by_id="7938C59B-88BF-4B40-8F3A-C77813A7AFF1")
		# obj = self._manager_api.get_resources_by_criterion(self._session_id, criterion)

		print(obj)
		# for mid in obj['members']:
		# 	member = self._manager_api.get_resource(self._session_id, by_id=mid)
		# 	print(member['name'])

	def logout(self):
		self._manager_api.close_session(self._session_id)
		for server_id in self._blob_server_sessions:
			session_id, api = self._blob_server_sessions[server_id]
			api.close_session(session_id)
		self._blob_server_sessions = {}
		self._session_id = None
		self._model_server_urls = {}

	@staticmethod
	def to_unique(name):
		return f'{name}_{random.choice(CHARS)}{random.choice(CHARS)}{random.choice(CHARS)}{random.choice(CHARS)}'
