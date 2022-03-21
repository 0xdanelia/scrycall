from scry_cache import UrlCardCache, CardCache
import time
import requests
import requests.utils

URL_CACHE = UrlCardCache()
CARD_CACHE = CardCache()


def get_cards_from_query(query) -> list[str]:
    """Get a list of cards from a query string

    Args:
        query: query string

    Returns:
        List of cards
    """
    url = f"https://api.scryfall.com/cards/search?q={requests.utils.requote_uri(query)}"
    card_list = load_cards(url)
    return card_list


# TODO: this makes some assumptions about the shape of the data
# TODO: make this less clunky
def get_uri_attribute(url):
    """Call an api url found nested in the card data

    Args:
        url: url

    Returns:
        json data
    """
    json_data = URL_CACHE.load_item(url)
    if json_data == None:
        json_data = get_api_data_from_url(url)
        URL_CACHE.store_url(url, [json_data])
    else:
        json_data = CARD_CACHE.load_item(json_data[0])
    return json_data


def get_card_from_uuid(uuid: str) -> dict:
    """Get a single card from the api.

    Args:
        uuid: Scryfall UUID

    Returns:
        JSON data
    """
    return get_cards_from_json_data(
        get_api_data_from_url(f"https://api.scryfall.com/cards/{uuid}")
    )


def get_cards_from_json_data(data):
    """Get a list of cards from the api json data.

    Args:
        data: Card JSON data from Scryfall

    Returns:
        List of card
    """
    cards = data["data"]
    if data["has_more"]:
        next_url = data["next_page"]
        cards += load_cards(next_url)
    return cards


def load_cards(url, use_cache: bool = True) -> list[str]:
    """Load cards

    Args:
        url: URL to load from
        use_cache: Enable the use of the cache

    If the card does not exist in the cache, it is queried for.
    """
    # the query url is tied to a list of card ids
    # each card id is tied to cached json data for the card itself
    cards = []
    if use_cache:
        try:
            for card_uid in URL_CACHE.load_item(URL_CACHE.__class__.uid(url)):
                card = CARD_CACHE.load_item(card_uid)
                if not card:
                    card = get_card_from_uuid(card_uid.split["_"][-1])
                    if card:
                        CARD_CACHE.store_card(card)
                cards.append(card)
        except:
            pass
    if not cards:
        json_data = get_api_data_from_url(url)
        if json_data:
            cards = get_cards_from_json_data(json_data)
            if use_cache:
                URL_CACHE.store_url(url, cards)
    return cards


def get_api_data_from_url(url) -> dict:
    """Call the api and return the data

    100ms delay between calls per https://scryfall.com/docs/api
    """
    time.sleep(0.1)
    resp = requests.get(url)
    if not resp.ok:
        print(resp.text)
        return {}
    return resp.json()
