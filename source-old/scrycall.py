import sys
import scryparse

try:
	options = {'format' : '%n', 'null' : '', 'null-format' : ''}
	
	# handle incoming input from pipe
	piped = ''
	if not sys.stdin.isatty():
		piped = ' '.join(item.rstrip() for item in sys.stdin.readlines())
		
	# handle command line arguments
	query = scryparse.parseargs(sys.argv, piped, options)
	
	# get a collection of card objects that match the query
	cards = scryparse.getcards(query, options)

	colsizes = [0]
	printcols = []
	for card in cards:
		# if a card property is null or empty, print this instead
		ifnull = scryparse.getifnull(card, options)
		
		# if formatstring contains %[*], we might print multiple lines per card
		for line in scryparse.iterateformat(card, options['format'], options):
			# replace the %X placeholders with card properties
			cols = scryparse.printline(card, scryparse.formatstring(line), options, ifnull)
			# if formatstring contains %|, measure column widths
			if len(cols) > 1:
				for c in range(len(cols)):
					columnlength = len(cols[c])
					if c > len(colsizes) - 1:
						colsizes.append(columnlength)
					elif colsizes[c] < columnlength:
						colsizes[c] = columnlength
			printcols.append(cols)

	for col in printcols:
		colstring = ''
		# if multiple columns, format line with column widths
		if len(col) > 1:
			for i in range(len(col)):
				if colsizes[i] > 0:
					colstring = colstring + '{' + str(i) + ':' + str(colsizes[i]) + '}'
			toprint = colstring.format(*col).rstrip()
			if toprint != '':
				print(colstring.format(*col).rstrip())
		elif col[0] != '':
			print(col[0])
	# make sure any threads started for cache writing are able to finish
	scryparse.waitforthreads()

except Exception as ex:
	print(ex)
