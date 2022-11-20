#!/usr/bin/env python
import sys

from scry_args import parse_args
from scry_data import get_cards_from_query
from scry_output import print_data
from scry_exception import ScrycallArgException, ScrycallApiException


def main():

    # query: string you would type in the search bar at scryfall.com
    # formatting: list of format strings that determine how data is printed
    try:

        query, formatting = parse_args(sys.argv[1:])

        if not query:
            return 0

        cards = get_cards_from_query(query)

        if not cards:
            return 0

        print_data(cards, formatting)

    except (ScrycallArgException, ScrycallApiException) as e:
        print(e)
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
