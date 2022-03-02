import os, json, hashlib

CACHE_DIR_API = os.path.expanduser('~') + '/.cache/scrycall/api/'
CACHE_DIR_CARD = os.path.expanduser('~') + '/.cache/scrycall/card/'


def write_cache_api(url, data):
	path = CACHE_DIR_API + hashlib.md5(url.encode()).hexdigest()
	write_cache_to_path(path, data)


def write_cache_card(id, data):
	path = CACHE_DIR_CARD + id
	write_cache_to_path(path, data)


def load_cache_api(url):
	path = CACHE_DIR_API + hashlib.md5(url.encode()).hexdigest()
	return load_cache_from_path(path)


def load_cache_card(id):
	path = CACHE_DIR_CARD + id
	return load_cache_from_path(path)


def write_cache_to_path(path, data):
	check_cache_dirs()
	with open(path, 'w') as cachefile:
		json.dump(data, cachefile)


def load_cache_from_path(path):
	check_cache_dirs()
	try:
		with open(path, 'r') as cachefile:
			return json.load(cachefile)
	except:
		return None

def check_cache_dirs():
	if not os.path.isdir(CACHE_DIR_API):
		os.makedirs(CACHE_DIR_API)
	if not os.path.isdir(CACHE_DIR_CARD):
		os.makedirs(CACHE_DIR_CARD)
