# parse command line input
def parse_args(args):
    query = None
    flags = {}
    formatting = None
    
    for arg in args:
        # arg is a flag
        if arg.startswith('--'):
            flag, value = parse_flag(arg)
            flags[flag] = value
        # arg is part of the query
        else:
            if query == None:
                query = parse_query(arg)
            else:
                query = query + ' ' + parse_query(arg)
    
    # default formatting
    formatting = flags.get('format')
    if formatting == None:
        formatting = '%{name} %| %{type_line} %| %{mana_cost}'
    
    return query, flags, formatting


# parse flags from the command line and get their value
def parse_flag(arg):
    if arg.startswith('--format='):
        flag = 'format'
        value = arg[9:]

    return flag, value


# parse query text from the command line
def parse_query(arg):
    # backticks are replaced with single quotes
    # otherwise the text is used as-is
    return arg.replace("`", "'")
