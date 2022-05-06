def parse_args(args):
    query = None
    formatting = []

    for arg in args:
        # arg is a flag
        flag_was_parsed = False
        if arg.startswith('--'):
            flag_was_parsed = parse_flag(arg, formatting)
        # arg is part of the query
        if not flag_was_parsed:
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
        return True
    elif arg.startswith('--else='):
        # if a formatted field has no value, instead use this as the print format
        value = arg[7:]
        if not formatting:
            raise 'Must have a "print=" flag before using "else="'
        formatting.append(value)
        return True
    return False


def parse_string(arg):
    # backticks are replaced with single quotes
    # otherwise the text is used as-is
    result = arg.replace("`", "'")
    return result
