#!/usr/bin/env python3
import sys

from scry_args import parse_args
from scry_data import get_cards_from_query
from scry_output import print_cards


def main():
    query, formatting = parse_args()

    cards = get_cards_from_query(query)
    print_cards(cards, formatting)

    return 0


if __name__ == "__main__":
    sys.exit(main())
