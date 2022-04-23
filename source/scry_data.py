from scry_api import get_api_url_from_query, get_api_data_from_url
from scry_cache import load_cache_url, load_cache_card, write_cache_url, write_cache_card


# get a list of cards from a query string
def get_cards_from_query(query):
    url = get_api_url_from_query(query)
    card_list = get_cards_from_url(url)
    return card_list


# get a list of cards from an api url
def get_cards_from_url(url):
    card_list = load_cards_from_cache(url)
    if card_list == None:
        json_data = get_api_data_from_url(url)
        card_list = get_cards_from_json_data(json_data)
        save_to_cache(url, card_list)
    return card_list            


# TODO: this makes some assumptions about the shape of the data
# TODO: make this less clunky
# call an api url found nested in the card data
def get_uri_attribute_from_url(url):
    json_data = load_cache_url(url)
    if json_data == None:
        json_data = get_api_data_from_url(url)
        write_cache_url(url, [json_data])
        write_cache_card(json_data)
    else:
        json_data = load_cache_card(json_data[0])
    return json_data


# get a single card from the api
def get_card_from_id(id):
    url = 'https://api.scryfall.com/cards/' + id
    card = get_api_data_from_url(url)
    write_cache_card(card)
    return card


# get a list of cards from the api json data
def get_cards_from_json_data(data):
    cards = data['data']
    if data['has_more']:
        next_url = data['next_page']
        cards += get_cards_from_url(next_url)
    return cards


# save card data to local cache
def save_to_cache(url, cards):
    # cache each card individully
    for card in cards:
        write_cache_card(card)
    # cache the list of card ids tied to the url
    write_cache_url(url, cards)


# load cards from local cache
def load_cards_from_cache(url):
    cached_card_ids = load_cache_url(url)
    if cached_card_ids == None:
        return None
    # the query url is tied to a list of card ids
    # each card id is tied to cached json data for the card itself
    cards = []
    for id in cached_card_ids:
        card = load_cache_card(id)
        # if a card isn't cached for some reason, query for it
        if card == None:
            card = get_card_from_id(id.split['_'][-1])
            if card == None:
                continue
        cards.append(card)
    return cards

