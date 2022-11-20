import json
import time
import urllib.error
import urllib.parse
import urllib.request

from scry_exception import ScrycallApiException


IS_FIRST_QUERY = True


def get_api_url_from_query(query):
    # transform the query string into a url-friendly format, and attach it to the scryfall api url
    api_url = 'https://api.scryfall.com/cards/search?q='
    return api_url + urllib.parse.quote_plus(query)


def get_api_data_from_url(url):
    global IS_FIRST_QUERY
    if not IS_FIRST_QUERY:
        # wait 100 milliseconds between calls to avoid spamming the api:  https://scryfall.com/docs/api
        time.sleep(0.1)
    else:
        IS_FIRST_QUERY = False

    try:
        with urllib.request.urlopen(url) as response:
            data = json.load(response)
    except urllib.error.HTTPError as exc:
        # scryfall returns an Error object for bad requests, which can be extracted from the exception
        data = json.load(exc)

        # need to raise some HTTP errors here to prevent them from being cached, otherwise scrycall will
        # load the error from the cache even after the problem is resolved:
        # 429 = rate limit exceeded. We want to allow the user to see new results after slowing their query rate.
        # 500+ = these are issues on the server-side, and will hopefully be only temporary.
        if exc.code == 429 or exc.code >= 500:
            error_msg = f'ERROR: HTTP {data.get("status")} {data.get("code")} - {data.get("details")}'
            for warning in data.get('warnings', []):
                error_msg += f'\nWARNING: {warning}'
            raise ScrycallApiException(error_msg)

    except urllib.error.URLError:
        raise ScrycallApiException('ERROR: Could not access https://api.scryfall.com')

    return data
