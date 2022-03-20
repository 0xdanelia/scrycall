import requests
import requests.utils
import time

# TODO: Refactor this module out (passthrough)

# get the web address for calling the scryfall api
def get_api_url_from_query(query):
    return f"https://api.scryfall.com/cards/search?q={requests.utils.requote_uri(query)}"


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
