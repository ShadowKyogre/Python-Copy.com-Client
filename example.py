import CopyComClient
from my_app_keys import *

if __name__ == "__main__":
	perms = {
		'links': {
			'read':True,
			'write':True,
		},
		"filesystem":{
			'read':True,
		}
	}
	client=CopyComClient(consumer_key, consumer_secret, perms=perms)
	resp=client.get_link()
	pprint.pprint(resp.status_code)
	pprint.pprint(resp.headers)
	pprint.pprint(resp.json())