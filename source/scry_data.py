from scry_api import get_api_url_from_query, get_api_data_from_url
from scry_cache import load_url_from_cache, write_url_to_cache
from scry_cache import CACHE_FLAGS


def get_cards_from_query(query):
    url = get_api_url_from_query(query)
    card_list = get_json_data_from_url(url)
    return card_list


def get_json_data_from_url(url):
    json_data = load_url_from_cache(url)
    if json_data is None:
        if CACHE_FLAGS['cache-only']:
            return []
        json_data = get_api_data_from_url(url)
        json_data = parse_json_data_into_list(json_data)
        write_url_to_cache(url, json_data)
    return json_data


def parse_json_data_into_list(data):
    if data is None:
        return []
    data_type = data.get('object')
    if data_type == 'list' or data_type == 'catalog':
        data_list = data.get('data')
        if data.get('has_more'):
            next_url = data.get('next_page')
            next_data = get_api_data_from_url(next_url)
            data_list += parse_json_data_into_list(next_data)
        return data_list
    else:
        return [data]
