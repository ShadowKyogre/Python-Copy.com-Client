#!/usr/bin/python
from requests_oauthlib import OAuth1Session
import webbrowser
import pprint
import json
import urllib.parse
import os.path

RTOKEN_URL    = "https://api.copy.com/oauth/request"
AUTHORIZE_URL = "https://www.copy.com/applications/authorize"
ACCESS_URL    = "https://api.copy.com/oauth/access"
HEADERS = {
		'X-Api-Version':'1',
		'Accept':'application/json'
	}

class CopyComClient:
	def __init__(self, consumer_key, consumer_secret, perms=None):
		self.oauth = OAuth1Session(consumer_key, 
							client_secret=consumer_secret,
							callback_uri="oob")

		if perms is not None:
			perms_str="{}?scope={}".format(RTOKEN_URL, 
								  urllib.parse.quote(json.dumps(perms)))
		else:
			perms_str=RTOKEN_URL

		self.token = self.oauth.fetch_request_token(perms_str) #get our token
		print("Our token:")
		pprint.pprint(self.token)

		auth_url = self.oauth.authorization_url(AUTHORIZE_URL)
		webbrowser.open(auth_url)
		accepted = ''
		while accepted == '':
			accepted = input('Paste full redirect URL here: ')

		auth_resp = self.oauth.parse_authorization_response(accepted)
		self.verifier = auth_resp.get('oauth_verifier')
		print("Our verification:")
		pprint.pprint(self.verifier)

		self.oauth = OAuth1Session(consumer_key, 
						client_secret = consumer_secret,
						resource_owner_key = self.token.get('oauth_token'),
						resource_owner_secret = self.token.get('oauth_token_secret'),
						verifier = self.verifier)
		try:
			self.token = self.oauth.fetch_access_token(ACCESS_URL) #get our real token
			print("Our updated token:")
			pprint.pprint(self.token)

			self.oauth = OAuth1Session(consumer_key, 
							client_secret = consumer_secret,
							resource_owner_key = self.token.get('oauth_token'),
							resource_owner_secret = self.token.get('oauth_token_secret'),
							verifier = self.verifier)
		except ValueError as e:
			print("Huh, seems we don't need to get a true token...")

	def user_profile(self,update_data = None):
		if update_data is None:
			return self.oauth.get('https://api.copy.com/rest/user', 
						 headers=HEADERS)
		else:
			return self.oauth.post('https://api.copy.com/rest/user', 
						  data=update_data, headers=HEADERS)

	def read_root(self):
		return self.oauth.get('https://api.copy.com/rest/meta', headers=HEADERS)
	
	def read_dir(self, path):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/meta/copy/', 
									path)
		return self.oauth.get(final_path, headers=HEADERS)
	
	def read_file_revs(self, path):
		revs = os.path.join(path,'/@activity')
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/meta/copy/', 
									revs)
		return self.oauth.get(final_path, headers=HEADERS)

	def read_file_revs(self, path, time):
		revs = os.path.join(path,'@activity','@time:{}').format(time)
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/meta/copy/', 
									revs)
		return self.oauth.get(final_path, headers=HEADERS)
	
	def download_file(self, path):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/files/', 
									path)
		return self.oauth.get(final_path, headers=HEADERS)

	def delete_file(self, path):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/files/', 
									path)
		return self.oauth.delete(final_path, headers=HEADERS)
	
	def rename_file(self, path, new_name, overwrite=True):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/files/',
									path)
		final_path += "?name={}".format(new_name)
		if overwrite:
			final_path += "&overwrite=true"
		else:
			final_path += "&overwrite=false"
		return self.oauth.put(final_path, headers=HEADERS)

	def move_file(self, path, new_path, overwrite=True):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/files/', 
									path)
		final_path += "?path={}".format(new_path)
		if overwrite:
			final_path += "&overwrite=true"
		else:
			final_path += "&overwrite=false"
		return self.oauth.put(final_path, headers=HEADERS)

	def create_file(self, path, file=None, overwrite=True): # work on uploading folders later
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/files/', 
									path)
		if overwrite:
			final_path += "&overwrite=true"
		else:
			final_path += "&overwrite=false"
		if file is None:
			return self.oauth.post(final_path)
		else:
			f={'file':(file,open(file, 'rb'))}
			return self.oauth.post(final_path, files=f)

	def get_link(self, token=None):
		if token is None:
			return self.oauth.get('https://api.copy.com/rest/links',
						 headers=HEADERS)
		else:
			final_path = urllib.parse.urljoin('https://api.copy.com/rest/links/', 
									 token)
			return self.oauth.put(final_path, headers=HEADERS)
	
	def create_link(self, public, name, paths):
		data = { 'public':public,
			'name':name,
			'paths':paths,
			}
		return self.oauth.post('https://api.copy.com/rest/links', data=data)
	
	def update_link(self, public, name, paths, token):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/links/', 
									token)
		data = { 'public':public,
			'name':name,
			'paths':paths,
			}
		return self.oauth.put(final_path, data=data)
	
	def update_link_recipients(self, token, add_emails, remove_emails):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/links/', 
									token)
		data = { 'recipients':[]}
		data.extend([{'email':e,'remove':True} for e in remove_emails])
		data.extend([{'email':e,'permissions':'read'} for e in add_emails])
		return self.oauth.put(final_path, data=data)

	def delete_link(self, token):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/links/', 
									token)
		return self.oauth.delete(final_path)
	
	def get_linked_files(self, token):
		final_path = urllib.parse.urljoin('https://api.copy.com/rest/meta/links/', 
									token)
		return self.oauth.get(final_path)
