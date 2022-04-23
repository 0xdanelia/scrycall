import os, time, json, hashlib, threading

cachedir = os.path.expanduser('~') + '/.cache/scrycall/'
cachelimit = 86400 # 24 hours

# object to handle cache for a particular query
class CacheFile:

    def __init__(self, url):
        # make sure the cache directory exists
        checkcachedir()
        # cache file name is a hash of the api query
        self.file = hashlib.md5(url.encode()).hexdigest()
        self.path = cachedir + self.file
        self.exists = os.path.isfile(self.path)
        self.writethread = None
    
    # check if cached data has become stale
    def isexpired(self):
        return time.time() - os.path.getmtime(self.path) > cachelimit
    
    # load json from a saved cache file
    def read(self):
        with open(self.path, 'r') as cachefile:
            return json.load(cachefile)
    
    # spin up a thread to write json to a cache file
    def write(self, data):
        if self.writethread != None:
            self.writethread.join()
        self.writethread = threading.Thread(target=write_threaded, args=(self.path, data), daemon=True)
        self.writethread.start()
    
    # delete the cache file
    def delete(self):
        os.remove(self.path)
        self.exists = False

# make sure the directory to save cache files exists
def checkcachedir():
    if not os.path.isdir(cachedir):
        os.makedirs(cachedir)

# delete all cache files older than a specified time
def cleancache(expiretime=cachelimit):
    now = time.time()
    if os.path.isdir(cachedir):
        for file in os.listdir(cachedir):
            if now - os.path.getmtime(cachedir + file) > expiretime:
                os.remove(cachedir + file)

# delete all cache files
def deletecache():
    cleancache(0)

# write json to file (intended for new threads)
def write_threaded(path, data):
    with open(path, 'w') as cachefile:
        json.dump(data, cachefile)
