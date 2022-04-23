import urllib.request, urllib.parse, json, time

apiurl = 'https://api.scryfall.com/cards/search?q='
lastquerytime = 0

# get the web address for calling the scryfall api
def geturl(query):
    return apiurl + urllib.parse.quote_plus(query)

# call the api and return the data
def getdata(url):
    global lastquerytime

    # don't query too often, be kind to the scryfall devs
    diff = 0.1 - (time.time() - lastquerytime)
    if diff > 0:
        t1 = time.time()
        time.sleep(diff)
    
    data = json.load(urllib.request.urlopen(url))
    lastquerytime = time.time()
    return data
