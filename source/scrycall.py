#!/usr/bin/env python
import sys

from scry_args import parse_args
from scry_data import get_cards_from_query
from scry_output import print_data


def main():

    # query: string you would type in the search bar at scryfall.com
    # formatting: list of format strings that determine how data is printed
    query, formatting = parse_args(sys.argv[1:])

    cards = get_cards_from_query(query)
    print_data(cards, formatting)

    return 0


if __name__ == '__main__':
    sys.exit(main())
