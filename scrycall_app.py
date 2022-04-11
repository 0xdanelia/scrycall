#!/usr/bin/env python3
import sys

from scrycall.scry_args import parse_args
from scrycall.scry_data import get_cards_from_query
from scrycall.scry_output import print_cards, CUSTOM_NULL


def main() -> int:
    args = parse_args(sys.argv[1:])

    CUSTOM_NULL = args.null

    cards = get_cards_from_query(args.query)
    print_cards(cards, args.formatting)

    return 0


if __name__ == "__main__":
    sys.exit(main())
