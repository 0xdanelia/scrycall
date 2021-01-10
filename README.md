## Scrycall
A linux command line tool for querying the scryfall.com API


### What does Scrycall do?
Scrycall makes it easy to search for MTG cards from the linux command line. It prints the card information of your choice to the terminal, allowing for easy integration with other linux tools using pipes. Scrycall uses https://scryfall.com/ to query for cards which are returned as JSON objects. You can parse the JSON using special format parameters (see below) to print any information you want about the cards you query.

Scrycall also stores the JSON data in a local cache at `~/.cache/scrycall/` to quickly access for repeated queries. The data is considered stale after 24 hours and Scrycall will automatically query the API again for a refresh if you try to use stale data. You can manage your cache using some command line arguments (see below).


### How do I install Scrycall?
You can download the project using the command `git clone https://github.com/0xdanelia/scrycall`

The project comes with a pre-compiled executable. You can compile the code yourself if you want using https://www.pyinstaller.org/

You can run it using the command `path/to/scry [ARGS]` 

Alternatively if you copy the file somewhere in your `$PATH` then you can just use `scry [ARGS]`

You can also just run the python source script using the command `python /path/to/scrycall.py [ARGS]`


### How do I use Scrycall?

First familiarize yourself with the Scryfall search syntax at https://scryfall.com/docs/syntax

Then simply run Scrycall using your plain text search query as the arguments.
```
> scry venser t:creature
Venser, Shaper Savant
Venser's Sliver
```
```
> scry o:"counter target noncreature spell unless"
Concerted Defense
Disciple of the Ring
Izzet Charm
Spell Pierce
Stubborn Denial
```

### What else can I print about a card?

You can use the argument `--format=` or `--f=` to print different information about the cards that the query returns. Within the format string  `%` is a special character used to indicate certain parameters based on the JSON card objects. Be sure to surround your format string in quotes "" if it contains any whitespace. The special parameters are:
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
> scry counterspell --format="%n  %m  [%o]"
Counterspell  {U}{U}  [Counter target spell.]
```

You can also parse the raw JSON yourself by putting the attribute names inside `%[]` and using `;` to separate multiple attributes.
```
> scry "lightning bolt" --format="%[legalities;modern]"
legal
```

To print all available property names, use `?` in the brackets.
```
> scry "black lotus" --format="%[prices;?]"
['eur', 'eur_foil', 'tix', 'usd', 'usd_foil']
```

To iterate every property of a json object, use `*` in the brackets. This may print multiple lines for each card.
```
> scry "serra angel" --format="%[keywords;*]"
Flying
Vigilance
```

You can print the name of the previous property using `^` within the brackets. This can be useful when combined with iterating.
```
> scry "scalding tarn" --format="%[prices;*;^] %| $%[prices;*]"
usd       $55.63
usd_foil  $102.86
eur       $46.00
eur_foil  $81.50
tix       $21.14
```

Some properties are web addresses for an api call to another object. The api will automatically be called (and cached) and you can traverse the retrieved object as normal.
```
> scry "mox lotus" --f="%[set_uri;name] was released %[set_uri;released_at]"
Unhinged was released 2004-11-19
```

### What other arguments are there?

`--null=` or `--n=`

When a card property in `--format=` is null or empty, print this custom output in its place. This string can use the same `%` format characters as `--format=` except it cannot contain `%|` for column seperation or `%[*]` for iterating. If this text contains any null or empty properties, print "" in its place.

`--cache-only` or `--c`

Query your local cache only. Do not query the api even if cache is stale.

`--ignore-cache` or `--i`

Query the api only. Do not query cache even if api can not be reached.

`--do-not-cache` or `--d`

Do not write fresh api data to your local cache.

`--clean-cache`

Search the local cache and delete any stale data.

`--delete-cache`

Delete everything from the local cache.

`--help` or `--h`

Print some helpful information like you see here.

`--help-format`

Print helpful information specific to the `--format=` and `--null=` argument syntax.


