def print_help():
    #####('--------------------------------------------------------------------------------') 80
    print('')
    print('Special flags begin with "--" and can appear anywhere in the input.')
    print('Everything else will be treated as part of the query string.')
    print('Query syntax reference: https://scryfall.com/docs/syntax')
    print('')
    print('--print="CUSTOM OUTPUT TEXT"')
    print('    Set the format of the output. Use %X to print certain card properties.')
    print('    Default is "%{name} %| %{type_line} %| %{mana_cost}".')
    print('    Use --help-format for more information.')
    print('')
    print('--else="CUSTOM OUTPUT TEXT"')
    print('    When a property in --print="" is not available, then instead try to')
    print('    print the contents in the --else="" flag. Multiple --else="" flags can')
    print('    be used in case one of them also contains a property that is unavailable.')
    print('')
    print('--cache-only')
    print('    Query your local cache only. Do not query the api even if cache is stale.')
    print('')
    print('--ignore-cache')
    print('    Query the api only. Do not query cache even if api can not be reached.')
    print('')
    print('--do-not-cache')
    print('    Do not write new api data to your local cache.')
    print('')
    print('--clean-cache')
    print('    Delete any stale data from the local cache.')
    print('')
    print('--delete-cache')
    print('    Delete everything from the local cache.')
    print('')
    #####('--------------------------------------------------------------------------------') 80


def print_help_format():
    #####('--------------------------------------------------------------------------------') 80
    print('')
    print('The --print="" string is what this program will print after finishing the query.')
    print('Use %X to print card properties. Everything else will be printed as written.')
    print('These properties come from the JSON card objects returned by the api.')
    print('The --else="" string will be printed instead if any property is unavailable.')
    print('')
    print('%n    name')
    print('%m    mana_cost')
    print('%c    cmc  (converted mana cost)')
    print('%y    type_line')
    print('%p    power')
    print('%t    toughness')
    print('%l    loyalty')
    print('%o    oracle_text')
    print('%f    flavor_text')
    print('%%    this will print a literal % instead of interpreting a special character')
    print('%|    this will separate output into nicely spaced columns')
    print('')
    print('To reference a property of the JSON card object that is not listed above,')
    print('put the name of that property inside "%{}". To traverse multiple objects,')
    print('separate their names with "." within the brackets.')
    print('$ scry "lightning bolt" --print="%{legalities.modern}"')
    print('')
    print('To print all available property names, use "?" in the brackets.')
    print('$ scry lightning bolt --print="%{prices.?}"')
    print('')
    print('To iterate every property of a JSON object, use "*" in the brackets.')
    print('This may print multiple lines for each card returned by the query.')
    print('$ scry lightning bolt --print="%{image_uris.*}"')
    print('')
    print('You can print the name of the previous property using "^" within the brackets.')
    print('This can be useful when combined with iterating.')
    print('$ scry lightning bolt --print="%{prices.*.^}  %| %{prices.*}"')
    print('')
    print('Some properties are web addresses for an api call to another object. You can')
    print('call the api and continue parsing by using a "/". This will always return a')
    print('list, which you can iterate through with "*" or with a specific index.')
    print('$ scry lightning bolt --print="%{set_uri./.*.name}"')
    print('')
    #####('--------------------------------------------------------------------------------') 80