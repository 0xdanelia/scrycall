import os, json, hashlib, re


CACHE_DIR = os.path.expanduser('~') + '/.cache/scrycall/'
CACHE_DIR_URL = CACHE_DIR + 'url/'


def write_url_to_cache(url, data_list):
    path = CACHE_DIR_URL + get_url_cache_name(url)
    cached_data_files = []
    for data in data_list:
        # save each data object in its own file, then save a list of those filenames
        write_json_to_cache(data)
        cached_data_files.append(get_cache_path_from_object(data))
    url_data_to_cache = {'url': url, 'files': cached_data_files}
    _write_to_cache(path, url_data_to_cache)


def write_json_to_cache(data):
    path = CACHE_DIR + get_cache_path_from_object(data)
    _write_to_cache(path, data)


def _write_to_cache(path, data):
    dir_path = os.path.split(path)[0]
    if not os.path.isdir(dir_path):
        os.makedirs(dir_path)
    with open(path, 'w') as cachefile:
        json.dump(data, cachefile, indent=4)


def load_url_from_cache(url):
    path = CACHE_DIR_URL + get_url_cache_name(url)
    # url caches contain a list of filenames, where each file contains cached JSON data
    cached_data = _load_from_cache(path)
    if not cached_data:
        return None
    cache_filenames = cached_data.get('files')
    if not cache_filenames:
        return None
    data = []
    for filename in cache_filenames:
        data.append(load_json_from_cache(filename))
    return data


def load_json_from_cache(filename):
    path = CACHE_DIR + filename
    return _load_from_cache(path)


def _load_from_cache(path):
    try:
        with open(path, 'r') as cachefile:
            return json.load(cachefile)
    except:
        return None


def get_url_cache_name(url):
    # each cached url gets a unique filename
    # to avoid issues with long urls and/or special characters, a hash is used instead of the url string
    return hashlib.md5(url.encode()).hexdigest()


def get_cache_path_from_object(obj):
    # organize cache by object type, and construct a unique filename for each object type
    # see: "TYPES & METHODS" https://scryfall.com/docs/api/
    obj_name = ''
    obj_id = ''
    obj_type = obj.get('object', 'None')

    if obj_type == 'card' or obj_type == 'set':
        obj_name = obj.get('name', '')
        obj_id = obj.get('id', '')

    elif obj_type == 'ruling':
        obj_name = hashlib.md5(obj.get('comment', '').encode()).hexdigest()
        obj_id = obj.get('oracle_id', '')

    # to avoid potential issues with filenames, only use letters, numbers, '_', and '-'
    obj_name = obj_name.replace(' ', '_')
    obj_name = re.sub('[^a-zA-Z0-9_]', '-', obj_name)

    return f'{obj_type}/{obj_name}_{obj_id}'
