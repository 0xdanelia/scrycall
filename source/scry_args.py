import sys
import argparse
import scry_output
from scry_output import Attributes

# parse command line input
def parse_args() -> tuple[str, str]:
    """Parse command line arguments

    Args:
        args: sys argv

    Returns:
        query: string you would type in the search bar at scryfall.com
        formatting: Card output line (with attribute placeholders)
    """
    parser = argparse.ArgumentParser(
        description="Scryfall CLI",
        epilog="""
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
        """,
    )
    parser.add_argument(
        "query",
        nargs="*",
        metavar="query",
        default=[],
        help="Scryfall query",
    )
    parser.add_argument(
        "-f",
        "--format",
        dest="formatting",
        type=str,
        default=f"{Attributes.NAME.value} %| {Attributes.TYPE_LINE.value} %| {Attributes.CMC.value}",
    )
    parser.add_argument(
        "--null",
        dest="null",
        default="",
        help="Print this value when NULL is the property value",
    )
    args = parser.parse_args()
    query = " ".join(args.query)

    query.replace("`", "'")
    scry_output.CUSTOM_NULL = args.null

    if not query:
        parser.print_help()
        sys.exit(0)

    return query, args.formatting
