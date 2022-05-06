## Scrycall
A command line tool for querying the scryfall.com API for Magic cards.

Scrycall makes it easy to search for MTG cards from the command line. It prints the card information of your choice to the terminal, allowing for easy integration with other command line tools using pipes. Scrycall uses https://scryfall.com/ to query for cards which are returned as JSON objects. You can parse the JSON using special format parameters (see below) to print any information you want about the cards you query.

Scrycall also stores the JSON data in a local cache at `~/.cache/scrycall/` to quickly access for repeated queries.


### How to run Scrycall
You can download the project using the command `git clone https://github.com/0xdanelia/scrycall`

You can run it using the command `python scry.py [ARGS]`


### How to query with Scrycall

First familiarize yourself with the Scryfall search syntax at https://scryfall.com/docs/syntax

Then simply run Scrycall using your plain text search query as the arguments. The below examples are from a `bash` shell. Exact formatting may vary slightly between shells. You can use a backtick `` ` `` in place of an apostrophe when making your query as well.
```
$ python scry.py venser t:creature
Venser, Shaper Savant  Legendary Creature — Human Wizard  {2}{U}{U}
Venser's Sliver        Artifact Creature — Sliver         {5}
```
```
$ python scry.py 'Urza`s rage'
Urza's Rage  Instant  {2}{R}
```
```
$ python scry.py 'o:"counter target noncreature spell unless"'
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
$ python scry.py '!"time walk"' set:alpha --print="%{image_uris.large}" | xargs wget -O "time_walk.jpg"
```
The Scryfall.com developers request that you add a delay of 50-100 milliseconds when making multiple rapid calls to the api. Scrycall automatically adds this delay between multiple calls within the program, but you are on your own when making calls elsewhere.

### How to format output

You can use the flag `--print=` to print different information about the cards that the query returns. Within the format string `%` is a special character used to indicate certain parameters based on the JSON card objects. The special parameters are:
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
$ python scry.py counterspell --print="%n  %m  [%o]"
Counterspell  {U}{U}  [Counter target spell.]
```

You can also parse the raw JSON yourself by putting the attribute names inside `%{}` and using `.` to separate multiple attributes.
```
$ python scry.py lightning bolt --print="%{legalities.modern}"
legal
```

To print all available property names as a list, use `?`. This can be helpful while constructing your format string.
```
$ python scry.py lightning bolt --print="%{prices.?}"
['usd', 'usd_foil', 'usd_etched', 'eur', 'eur_foil', 'tix']
```

To access a specific element of a list, you can reference its index as a number. Indexes begin at 0.
```
$ python scry.py '"serra angel"' --print="%{keywords}"
['Flying', 'Vigilance']
```
```
$ python scry.py '"serra angel"' --print="%{keywords.0}"
Flying
```

To iterate every property of a json object, use `*`. This may print multiple lines for each card.
```
$ python scry.py '"serra angel"' --print="%{keywords.*}"
Flying
Vigilance
```

You can print the name of the previous property using `^`. This can be useful when combined with iterating.
```
$ python scry.py scalding tarn --print="%{prices.*.^}  %|%{prices.*}"
usd       26.90
usd_foil  31.71
eur       24.91
eur_foil  37.99
tix       6.78
```

Some properties are urls for an api call to another object. You can call the api and continue parsing by using a `/`. This will always return a list, which you can iterate through with `*` or with a specific index.
```
$ python scry.py mox lotus --print="The set %{set_uri./.*.name} was released %{set_uri./.*.released_at}"
The set Unhinged was released 2004-11-19
```

If you try to print a property that does not exist for a card, instead nothing will be printed for that card.
You can add the flag `--else=` to print something else instead. This flag takes a format string just like `--print=`. You can chain together any number of `--else=` flags.
```
$ python scry.py venser --print="%n %| Loyalty: %|[%l]" --else="%n %| Power: %|<%p>"
Venser, Shaper Savant  Power:   <2>
Venser's Sliver        Power:   <3>
Venser, the Sojourner  Loyalty: [3]
```

