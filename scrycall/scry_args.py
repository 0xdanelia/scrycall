import argparse
from .scry_output import Attributes


class ArgumentError(Exception):
    """Error with input arguments"""


def parse_args(args: list) -> argparse.Namespace:
    """Parse command line arguments

    Args:
        args: sys argv

    Returns:
        parsed_args: Args namespace
    """
    parser = _parser()
    parsed_args = parser.parse_args(args)

    parsed_args.query = " ".join(parsed_args.query)
    parsed_args.query.replace("`", "'")

    if not parsed_args.query:
        parser.print_help()
        raise ArgumentError("No query provided!")

    return parsed_args


def _parser() -> argparse.ArgumentParser:
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
    return parser
