import sys

from scry_cache import clean_cache, delete_cache
from scry_cache import CACHE_FLAGS
from scry_help import print_help, print_help_format
from scry_output import PRINT_FLAGS


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
            raise Exception('ERROR: "print=" flag already set')
        formatting.append(value)
        return True
    elif arg.startswith('--else='):
        # if a formatted field has no value, instead use this as the print format
        value = arg[7:]
        if not formatting:
            raise Exception('ERROR: Must have a "print=" flag before using "else="')
        formatting.append(value)
        return True
    elif arg == '--no-dfc-parse':
        # turn off smart parsing for dual-faced-cards
        PRINT_FLAGS['dfc-smart-parse'] = False
        return True
    elif arg == '--dfc-default-front':
        # default to the front face of a dfc
        if PRINT_FLAGS['dfc-default-face'] is not None:
            raise Exception('ERROR: "dfc-default-face" can only be set once')
        PRINT_FLAGS['dfc-default-face'] = 0
        return True
    elif arg == '--dfc-default-back':
        # default to the back face of a dfc
        if PRINT_FLAGS['dfc-default-face'] is not None:
            raise Exception('ERROR: "dfc-default-face" can only be set once')
        PRINT_FLAGS['dfc-default-face'] = 1
        return True
    elif arg == '--cache-only':
        # do not query the api, only look at the cache
        if CACHE_FLAGS['ignore-cache']:
            raise Exception('ERROR: Cannot use both "ignore-cache" and "cache-only"')
        CACHE_FLAGS['cache-only'] = True
        return True
    elif arg == '--ignore-cache':
        # do not look at the cache, query the api regardless
        if CACHE_FLAGS['cache-only']:
            raise Exception('ERROR: Cannot use both "cache-only" and "ignore-cache"')
        CACHE_FLAGS['ignore-cache'] = True
        return True
    elif arg == '--do-not-cache':
        # do not save the query results to the cache
        CACHE_FLAGS['do-not-cache'] = True
        return True
    elif arg == '--clean-cache':
        clean_cache()
        return True
    elif arg == '--delete-cache':
        delete_cache()
        return True
    elif arg == '--help':
        print_help()
        sys.exit(0)
    elif arg == '--help-format':
        print_help_format()
        sys.exit(0)
    return False


def parse_string(arg):
    # backticks are replaced with single quotes
    # otherwise the text is used as-is
    result = arg.replace("`", "'")
    return result
