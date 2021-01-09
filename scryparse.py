import sys, time
import scrycache, scryapi, scryhelp
filecache = []

# get collection of json card objects based on query
def getcards(query, options):
	url = scryapi.geturl(query)
	return getdata(url, options)

# let any lingering threads finish their job
def waitforthreads():
	for cache in filecache:
		if cache.writethread != None:
			cache.writethread.join()

# extract json from local cache or api call
def getdata(url, options):
	global filecache
	# don't bother creating a cache object if we don't need to access the cache
	if not ('ignore-cache' in options and 'do-not-cache' in options):
		cachefile = scrycache.CacheFile(url)
		filecache.append(cachefile)

	# check for an existing, non-expired cache file
	dataloaded = False
	if 'ignore-cache' not in options:
		if cachefile.exists:
			if 'cache-only' in options or not cachefile.isexpired():
				try:
					data = cachefile.read()
					return data
				except:
					return []
	# if data not cached, query the api
	if 'cache-only' not in options:
		try:
			apidata = scryapi.getdata(url)
			if 'data' in apidata:
				data = apidata['data']
				# iterate through multiple calls for large data sets
				while apidata['has_more']:
					apidata = scryapi.getdata(apidata['next_page'])
					data = data + apidata['data']
			else:
				data = apidata
			# write data to local cache for quicker access next time
			if 'do-not-cache' not in options:
				cachefile.write(data)
			return data
		except:
			return []
	return []

# return data[key] if it makes sense to do so
def keyval(data, key, ifnull):
	try:
		val = None
		if key.isdigit():
			key = int(key)
		val = data[key]
		if val != None:
			return val
		return ifnull
	except:
		return ifnull

# if data is iteratable, get the list of keys or indexes
def getkeys(data):
	try:
		if isinstance(data, dict):
			keys = list(data.keys())
		else:
			keys = list(range(len(data)))
		return keys
	except:
		return []

# parse command line for option flags, while everything else becomes the query
def parseargs(args, piped, options):
	parsed = []
	for i in range(1, len(args)):
		arg = args[i]

		if arg.startswith('--'):
			parseoption(arg, options)
		else:
			# bash strips quotes from args, but we need them
			if ' ' in arg:
				arg = addquotes(arg)
			parsed.append(arg)
	if piped != '':
		parsed.append(piped)
	return ' '.join(parsed)

# do what the command line option is supposed to do
def parseoption(opt, options):
	# print some helpful info
	if opt == '--help' or opt == '--h':
		scryhelp.printhelp()
	elif opt == '--help-format':
		scryhelp.printhelpformat()
	# format the output and select card properties to print
	elif opt.startswith('--format=') or opt.startswith('--f='):
		options['format'] = opt[opt.index('=')+1:]
		
	# select what to print if a card property is null or empty
	elif opt.startswith('--null=') or opt.startswith('--n='):
		options['null'] = opt[opt.index('=')+1:]
		options['null-format'] = formatnull(options['null'])

	# if True, only check the local cache instead of querying api
	elif opt == '--cache-only' or opt == '--c':
		options['cache-only'] = True
		
	# if True, ignore existing cache and query for fresh data
	elif opt == '--ignore-cache' or opt == '--i':
		options['ignore-cache'] = True
		
	# if True, do not write results to local cache
	elif opt == '--do-not-cache' or opt == '--d':
		options['do-not-cache'] = True
	
	# delete expired cache files
	elif opt == '--clean-cache':
		scrycache.cleancache()
	
	# delete entire cache
	elif opt == '--delete-cache':
		scrycache.deletecache()
						
	# something unrecognized
	else:
		raise Exception('Invalid argument. Try --help for more information.')

# do our best to add quotes back into the query after bash strips them away
def addquotes(arg):	
	if arg.startswith('!'):
		return '!"' + arg[1:] + '"'
	elif ':' in arg:
		idx = arg.index(':')
		if idx < arg.index(' '):
			return arg[:idx] + ':"' + arg[idx+1:] + '"'
	return '"' + arg + '"'

# parse the custom format string into a list of tokens
def formatstring(formatstring):
	tokens = []
	string = formatstring
	while string != '':
		# card properties and special characters begin with '%'
		if '%' in string:
			p = string.index('%')
			if p > 0:
				tokens.append(string[:p])
			
			token = string[p:p+2]
			if token == '%[':
				closebracket = string.find(']', p+3)
				if closebracket < 0:
					raise Exception('Invalid format. Try --help-format for more information.')
				token = string[p:closebracket+1]
				string = string[closebracket+1:]
			else:
				token = tokenreplace(token)
				string = string[p+2:]
				
			tokens.append(token)
		# all other text will be printed as-is
		else:
			tokens.append(string)
			string = ''
	return tokens

# the string used to replace null or empty properties needs formatting too
def formatnull(nullstring):
	nulltokens = formatstring(nullstring)
	for t in nulltokens:
		if t == '%|' or (t.startswith('%[') and '*' in t):
			raise Exception('Invalid null format. Try --help-format for more information.')
	return nulltokens

# formatstring  shortcuts are replaced with the actual json key
def tokenreplace(token):
	if token == '%n':
		return '%name'
	if token == '%m':
		return '%mana_cost'
	if token == '%c':
		return '%cmc'
	if token == '%y':
		return '%type_line'
	if token == '%p':
		return '%power'
	if token == '%t':
		return '%toughness'
	if token == '%l':
		return '%loyalty'
	if token == '%o':
		return '%oracle_text'
	if token == '%f':
		return '%flavor_text'
	# %% is used to print a literal %, and %| divides output into columns
	if token == '%%' or token == '%|':
		return token
	raise Exception('Invalid format. Try --help-format for more information.')

# if formatstring contains %[*], print a new string for each card parameter
def iterateformat(card, formatstring, options):
	lines = []
	
	# replace '%%' with a unique placeholder that does not appear in formatstring
	percentplaceholder = '{PERCENT' + str(time.time()) + '}'
	while percentplaceholder in formatstring:
		percentplaceholder = '{PERCENT' + str(time.time()) + '}'
	# any remaining % will indicate a card property
	formatstring = formatstring.replace('%%', percentplaceholder)
	
	# find a %[] that contains a *
	toreplace = None
	toparse = formatstring
	while '%[' in toparse:
		startbracket = toparse.index('%[')
		endbracket = toparse.index(']', startbracket)
		bracketed = toparse[startbracket:endbracket+1]
		if '*' in bracketed:
			toreplace = bracketed[:bracketed.index('*')+1]
			break
		toparse = toparse[endbracket+1:]
	
	# return just the one string if no iterating is needed
	if toreplace == None:
		return [formatstring.replace(percentplaceholder, '%%')]
	
	# jsonparse returns a list of keys when it encounters the *
	keys = jsonparse(card, toreplace[2:].split(';'), options, [])
	
	# print the nullstring instead of iterating if card property is null
	if len(keys) == 0:
		newstring = formatstring.replace(bracketed, options['null'])
		lines = lines + iterateformat(card, newstring, options)
	else:
		# create a line for each key with the '*' replaced by the key
		for key in keys:
			newstring = formatstring.replace(toreplace, toreplace[:-1] + str(key))
			# recursively check the new formatstring for any more '*'s to iterate
			lines = lines + iterateformat(card, newstring, options)
	return lines

# replace any %X card properties in the nullstring for printing
def getifnull(card, options):
	return printline(card, options['null-format'], options, '')[0]

# parse %[] for json keys and traverse the card data for the specific value
def jsonparse(card, keys, options, ifnull):	
	val = card
	lastkey = ifnull
	for k in range(len(keys)):
		key = keys[k]
		# print the name of the previous key
		if key == '^':
			val = lastkey
		# print a list of available keys for the current object
		elif key == '?':
			val = sorted(getkeys(val))
		# return list of keys for iteration
		elif key == '*':
			return getkeys(val)
		else:
			# print the value of val[key] from the card object
			val = keyval(val, key, ifnull)
			# if the value is an api web address, query it for more data to traverse
			if isinstance(val, str) and val.startswith('https://') and key.endswith('uri'):
				lastkey = val
				val = getdata(val, options)
				continue
		lastkey = key
	if val == '':
		val = ifnull
	return val

# return the actual text that gets printed to the screen
def printline(card, params, options, ifnull):
	toprint = []
	cols = []
	
	for param in params:
		if param.startswith('%['):
			toprint.append(str(jsonparse(card, param[2:-1].split(';'), options, ifnull)))
		elif param == '%%':
			toprint.append('%')
		elif param == '%|':
			cols.append(''.join(toprint))
			toprint = []
		elif param.startswith('%'):
			toprint.append(str(keyval(card, param[1:], ifnull)))
		else:
			toprint.append(param)
	
	# return a list containing each column to be printed
	cols.append(''.join(toprint))
	return cols

