import json
import hashlib
import re
import pathlib

CACHE_DIR_URL = pathlib.Path.home() / ".cache/scrycall/api/"
CACHE_DIR_CARD = pathlib.Path.home() / ".cache/scrycall/card/"


def write_cache_url(url, cards):
    path = CACHE_DIR_URL / get_url_cache_name(url)
    ids = [get_card_cache_name(card) for card in cards]
    write_cache_to_path(path, ids)


def write_cache_card(card):
    path = CACHE_DIR_CARD / get_card_cache_name(card)
    write_cache_to_path(path, card)


def load_cache_url(url):
    path = CACHE_DIR_URL / get_url_cache_name(url)
    return load_cache_from_path(path)


def load_cache_card(id):
    path = CACHE_DIR_CARD / id
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
    """Create cache directories, if they don't exist"""
    for p in (CACHE_DIR_URL, CACHE_DIR_CARD):
        if not p.is_dir():
            p.mkdir(parents=True, exist_ok=True)


def get_url_cache_name(url):
    return hashlib.md5(url.encode()).hexdigest()


def get_card_cache_name(card):
    name = card["name"].replace(" ", "_")
    name = re.sub("[^a-zA-Z0-9_]", "-", name)
    return f"{name}_{card['id']}"
