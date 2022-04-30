import urllib.request, urllib.parse, json, time


first_query = True


# get the web address for calling the scryfall api
def get_api_url_from_query(query):
    api_url = 'https://api.scryfall.com/cards/search?q='
    return api_url + urllib.parse.quote_plus(query)


# call the api and return the data
def get_api_data_from_url(url):
    # wait 100 milliseconds between calls:  https://scryfall.com/docs/api
    global first_query
    if not first_query:
        time.sleep(0.1)
    else:
        first_query = False

    data = json.load(urllib.request.urlopen(url))
    return data
