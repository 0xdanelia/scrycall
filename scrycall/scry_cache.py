import os, json, hashlib, re

CACHE_DIR_URL = os.path.expanduser("~") + "/.cache/scrycall/api/"
CACHE_DIR_CARD = os.path.expanduser("~") + "/.cache/scrycall/card/"


def write_cache_url(url, cards):
    path = CACHE_DIR_URL + get_url_cache_name(url)
    ids = []
    for card in cards:
        ids.append(get_card_cache_name(card))
    write_cache_to_path(path, ids)


def write_cache_card(card):
    path = CACHE_DIR_CARD + get_card_cache_name(card)
    write_cache_to_path(path, card)


def load_cache_url(url):
    path = CACHE_DIR_URL + get_url_cache_name(url)
    return load_cache_from_path(path)


def load_cache_card(id):
    path = CACHE_DIR_CARD + id
    return load_cache_from_path(path)


def write_cache_to_path(path, data):
    check_cache_dirs()
    with open(path, "w") as cachefile:
        json.dump(data, cachefile, indent=4)


def load_cache_from_path(path):
    check_cache_dirs()
    try:
        with open(path, "r") as cachefile:
            return json.load(cachefile)
    except:
        return None


def check_cache_dirs():
    if not os.path.isdir(CACHE_DIR_URL):
        os.makedirs(CACHE_DIR_URL)
    if not os.path.isdir(CACHE_DIR_CARD):
        os.makedirs(CACHE_DIR_CARD)


def get_url_cache_name(url):
    return hashlib.md5(url.encode()).hexdigest()


def get_card_cache_name(card):
    name = card["name"].replace(" ", "_")
    name = re.sub("[^a-zA-Z0-9_]", "-", name)
    return name + "_" + card["id"]
