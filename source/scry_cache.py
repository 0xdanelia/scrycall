import os, json, hashlib, re

CACHE_DIR = os.path.expanduser('~') + '/.cache/scrycall/'
CACHE_DIR_URL = CACHE_DIR + 'url/'


def write_url_to_cache(url, data):
    path = CACHE_DIR_URL + get_url_cache_name(url)
    ids = []
    for obj in data:
        ids.append(get_cache_path_from_object(obj))
    write_to_cache(path, ids)


def write_json_to_cache(data):
    path = CACHE_DIR + get_cache_path_from_object(data)
    write_to_cache(path, data)


def get_cache_path_from_object(obj):
    obj_type = obj.get('object', 'misc')
    obj_name = obj.get('name', '').replace(' ', '_')
    obj_name = re.sub('[^a-zA-Z0-9_]', '-', obj_name)
    obj_id = obj.get('id')
    return f'{obj_type}/{obj_name}_{obj_id}'


def write_to_cache(path, data):
    dir_path = os.path.split(path)[0]
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(path, 'w') as cachefile:
        json.dump(data, cachefile, indent=4)


def load_url_from_cache(url):
    path = CACHE_DIR_URL + get_url_cache_name(url)
    return load_from_cache(path)


def load_json_from_cache(id):
    path = CACHE_DIR + id
    return load_from_cache(path)


def load_from_cache(path):
    try:
        with open(path, 'r') as cachefile:
            return json.load(cachefile)
    except:
        return None


def get_url_cache_name(url):
    return hashlib.md5(url.encode()).hexdigest()
