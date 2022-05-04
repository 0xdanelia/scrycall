def parse_args(args):
    query = None
    formatting = []

    for arg in args:
        # arg is a flag
        if arg.startswith('--'):
            parse_flag(arg, formatting)
        # arg is part of the query
        else:
            if query is None:
                query = parse_string(arg)
            else:
                query = query + ' ' + parse_string(arg)

    # default formatting
    if not formatting:
        formatting.append('%{name} %| %{type_line} %| %{mana_cost}')

    return query, formatting


def parse_flag(arg, formatting):
    if arg.startswith('--print='):
        # format the plain-text output
        value = arg[8:]
        if formatting:
            raise '"print=" flag already set'
        formatting.append(value)
    elif arg.startswith('--else='):
        # if a formatted field has no value, instead use this as the print format
        value = arg[7:]
        if not formatting:
            raise 'Must have a "print=" flag before using "else="'
        formatting.append(value)


def parse_string(arg):
    # backticks are replaced with single quotes
    # otherwise the text is used as-is
    result = arg.replace("`", "'")
    return result
