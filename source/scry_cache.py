import hashlib
import json
import os
import re
import time


CACHE_DIR = os.path.expanduser('~') + '/.cache/scrycall/'
CACHE_DIR_URL = CACHE_DIR + 'url/'

CACHE_FLAGS = {
    'cache-only': False,
    'ignore-cache': False,
    'do-not-cache': False,
}
# 24 hours == 86400 seconds
CACHE_EXPIRATION = 86400


def write_url_to_cache(url, data_list):
    if CACHE_FLAGS['do-not-cache']:
        return

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
    if CACHE_FLAGS['ignore-cache']:
        return None

    path = CACHE_DIR_URL + get_url_cache_name(url)

    if not os.path.isfile(path):
        return None

    # files older than the expiration time hours are considered stale and are not loaded
    last_modified_time = os.path.getmtime(path)
    now = time.time()
    if now > last_modified_time + CACHE_EXPIRATION:
        return None

    # url caches contain a list of filenames, where each file contains cached JSON data
    cached_data = _load_from_cache(path)
    if cached_data is None:
        return None
    cache_filenames = cached_data.get('files')
    if cache_filenames is None:
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
    # to avoid conflicts after special characters are removed, a hash of the original url is added
    hashed_url = hashlib.md5(url.encode()).hexdigest()
    trimmed_url = url.replace('https://api.scryfall.com/', '')
    trimmed_url = remove_special_characters(trimmed_url)

    # filenames are limited to 255 characters in many systems
    # md5 hashes are 32 characters long
    # limit the url portion of the filename to 220 characters, just to be safe
    if len(trimmed_url) > 220:
        trimmed_url = trimmed_url[:220]

    return f'{trimmed_url}_{hashed_url}'


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

    obj_name = remove_special_characters(obj_name)

    return f'{obj_type}/{obj_name}_{obj_id}'


def remove_special_characters(text):
    # to avoid potential issues with filenames, only use letters, numbers, '_', and '-'
    text = text.replace(' ', '_')
    text = re.sub('[^a-zA-Z0-9_]', '-', text)
    return text


def delete_cache():
    _remove_expired_files_from_cache(0)


def clean_cache():
    _remove_expired_files_from_cache(CACHE_EXPIRATION)


def _remove_expired_files_from_cache(expire_time):
    # delete files from cache that are older than expire_time (in seconds)
    now = time.time()
    if os.path.isdir(CACHE_DIR):
        for path, dirs, files in os.walk(CACHE_DIR):
            for filename in files:
                file_path = os.path.join(path, filename)
                if now > os.path.getmtime(file_path) + expire_time:
                    os.remove(file_path)
