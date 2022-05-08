# Scrycall
A command line tool for querying the scryfall.com API for Magic cards.

Scrycall makes it easy to search for MTG cards from the command line. It prints the card information of your choice to the terminal, allowing for easy integration with other command line tools using pipes. Scrycall uses https://scryfall.com/ to query for cards which are returned as JSON objects. You can parse the JSON using special format parameters (see below) to print any information you want about the cards you query.

Scrycall also stores the JSON data in a local cache at `~/.cache/scrycall/` to quickly access for repeated queries. Anything in the cache older than 24 hours is considered stale, and will automatically be replaced with fresh data from the api.


## How to run Scrycall
You can download the project using the command `git clone https://github.com/0xdanelia/scrycall`

The project comes with an executable zip file `scry` which can be run like any other Python script.
```
$ python scry [ARGS]
```
On Linux, this file can be copied to a location in your `$PATH` and then called like any other program.
```
$ scry [ARGS]
```

## How to build Scrycall
The project comes with a `build.py` script which creates an executable zip file of the source code.
```
$ python build.py
```


## How to query with Scrycall

First familiarize yourself with the Scryfall search syntax at https://scryfall.com/docs/syntax

Then simply run Scrycall using your plain text search query as the arguments. The below examples are from a `bash` shell. Exact formatting may vary slightly between shells. You can use a backtick `` ` `` in place of an apostrophe when making your query as well.
```
$ scry venser t:creature
Venser, Shaper Savant  Legendary Creature — Human Wizard  {2}{U}{U}
Venser's Sliver        Artifact Creature — Sliver         {5}
```
```
$ scry 'Urza`s rage'
Urza's Rage  Instant  {2}{R}
```
```
$ scry 'o:"counter target noncreature spell unless"'
Concerted Defense     Instant                  {U}
Decisive Denial       Instant                  {G}{U}
Disciple of the Ring  Creature — Human Wizard  {3}{U}{U}
Izzet Charm           Instant                  {U}{R}
Mage's Attendant      Creature — Cat Rogue     {2}{W}
Spell Pierce          Instant                  {U}
Stubborn Denial       Instant                  {U}
```

You can also pipe the output into another program. For example, use Scrycall to get the url of a card image, then pipe into wget to download and save the image.
```
$ scry '!"time walk"' set:alpha --print="%{image_uris.large}" | xargs wget -O "time_walk.jpg"
```
The Scryfall.com developers request that you add a delay of 50-100 milliseconds when making multiple rapid calls to the api. Scrycall automatically adds this delay between multiple calls within the program, but you are on your own when making calls elsewhere.

## How to format output

You can use the flag `--print=` to construct a format string to print information about the cards. The contents of this format string will be printed for each card. Within the format string `%` is a special character used to indicate certain card attributes based on the JSON card objects.
```
%n    name
%m    mana_cost
%c    cmc  (converted mana cost)
%y    type_line
%p    power
%t    toughness
%l    loyalty
%o    oracle_text
%f    flavor_text
%%    this will print a literal % instead of interpreting a special character
%|    this will separate output into nicely spaced columns
```
```
$ scry counterspell --print='Name: (%n)  -  Cost: [%m]  -  Text: "%o"'        
Name: (Counterspell)  -  Cost: [{U}{U}]  -  Text: "Counter target spell."
```

You can also parse the raw JSON yourself by putting the attribute names inside `%{}` and using `.` to separate multiple attributes.
```
$ scry lightning bolt --print="%{legalities.modern}"
legal
```

To print all available property names as a list, use `?`. This can be helpful while constructing your format string.
```
$ scry lightning bolt --print="%{prices.?}"
['usd', 'usd_foil', 'usd_etched', 'eur', 'eur_foil', 'tix']
```
```
$ scry lightning bolt --print="Price: $%{prices.usd}"
Price: $3.61
```

To access a specific element of a list, you can reference its index as a number. Indexes begin at 0.
```
$ scry '"serra angel"' --print="%{keywords}"
['Flying', 'Vigilance']
```
```
$ scry '"serra angel"' --print="%{keywords.0}"
Flying
```

To iterate every property of a json object, use `*`. This may print multiple lines for each card.
```
$ scry '"serra angel"' --print="%{keywords.*}"
Flying
Vigilance
```

You can print the name of the previous property using `^`. This can be useful when combined with iterating.
```
$ scry scalding tarn --print="%{prices.*.^}  %| %{prices.*}"
usd        26.90
usd_foil   31.71
eur        24.91
eur_foil   37.99
tix        6.78
```

Some properties are urls for an api call to another object. You can call the api and continue parsing by using a `/`. This will always return a list, which you can iterate through with `*` or with a specific index.
```
$ scry mox lotus --print="%{set_uri}"
https://api.scryfall.com/sets/4c8bc76a-05a5-43db-aaf0-34deb347b871
```
```
$ scry mox lotus --print="The set %{set_uri./.*.name} was released %{set_uri./.*.released_at}"
The set Unhinged was released 2004-11-19
```

If you try to print a property that does not exist for a card, instead nothing will be printed for that card.
You can add the flag `--else=` to print something else instead. This flag takes a format string just like `--print=`. You can chain together any number of `--else=` flags.
```
$ scry venser --print="%n %| Loyalty: %| <%l>" --else="%n %| Power: %| [%p]"
Venser, Shaper Savant  Power:    [2]
Venser's Sliver        Power:    [3]
Venser, the Sojourner  Loyalty:  <3>
```

## Other optional flags
```
--cache-only
    Query your local cache only. Do not query the api even if cache is stale.

--ignore-cache
    Query the api only. Do not query cache even if api can not be reached.

--do-not-cache
    Do not write new api data to your local cache.

--clean-cache
    Delete any stale data from the local cache.

--delete-cache
    Delete everything from the local cache.

--help
    Display some help, like you see here.

--help-format
    Display some help for formatting your --print="" and --else="" flags.
```
