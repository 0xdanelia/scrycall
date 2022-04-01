from enum import Enum
from typing import Optional, Union
import re
from collections import defaultdict

from scry_data import get_uri_attribute


class FormatError(Exception):
    """Error in the formatting string"""


class FormatAttributeError(Exception):
    """Invalid Attribute format"""


class Attributes(Enum):
    NAME = "%{name}"
    MANA_COST = "%{mana_cost}"
    CMC = "%{cmc}"
    TYPE_LINE = "%{type_line}"
    POWER = "%{power}"
    TOUGHNESS = "%{toughness}"
    LOYALITY = "%{loyalty}"
    ORACLE_TEXT = "%{oracle_text}"
    FLAVOR_TEXT = "%{flavor_text}"


# shortcuts for printing card attrobutes in the format string
ATTR_CODES = {
    "%n": Attributes.NAME.value,
    "%m": Attributes.MANA_COST.value,
    "%c": Attributes.CMC.value,
    "%y": Attributes.TYPE_LINE.value,
    "%p": Attributes.POWER.value,
    "%t": Attributes.TYPE_LINE.value,
    "%l": Attributes.LOYALITY.value,
    "%o": Attributes.ORACLE_TEXT.value,
    "%f": Attributes.FLAVOR_TEXT.value,
    "%|": "%{spacer}",
}
ATTR_DELIM = "."
CUSTOM_NULL = ""
SPACER_MARKER = "\n"
CARD_SUBLINES: dict[int, list] = defaultdict(
    list
)  # Hacky. Tracks the sublines for each card


def print_cards(cards: list[dict], formatting: str) -> None:
    """Print each card line-by-line

    Args:
        cards: _description_
        formatting (_type_): _description_
    """
    lines: list[str] = []
    base_line_idxs = []
    for card in cards:
        base_line_idxs.append(len(lines))  # Used to space newlines later
        for line in card_lines(card, formatting):
            lines.append(line)

    # Adjust column spacing
    for i in range(
        0, lines[base_line_idxs[0]].count(SPACER_MARKER)
    ):  # Number of newlines
        newline_idxs = []  # Only for base lines
        for i, idx in enumerate(base_line_idxs):
            newline_idxs.append(lines[idx].find(SPACER_MARKER))
        for i, idx in enumerate(base_line_idxs):
            # insert spaces to pad
            pad_amount = max(newline_idxs) - newline_idxs[i]
            lines[idx] = (
                lines[idx][: newline_idxs[i]]
                + " " * pad_amount
                + lines[idx][newline_idxs[i] :]
            )
            lines[idx] = lines[idx].replace(SPACER_MARKER, "", 1)

    for line in lines:
        print(line)


def attr_data(data: dict, attributes: list[Union[str, int]]):
    """Get data from a data structure, drilling down."""
    rval = data
    for attr in attributes:
        rval = rval[attr]
    return rval


def find_attrs(
    data: dict, attributes: list[str], attr_level: int, drill_values: list
) -> str:
    """Find the given attribute(s) within the given data

    Attribute Markers:
        ? = Available property names
        * = Iterate properties values

    Args:
        card: data
        attributes: List of attributes or attribute markers

    Returns:
        Attribute or ERR
    """
    value = ""
    attr = attributes[attr_level]
    prev_data = attr_data(data, drill_values)

    if attr == "*":
        # Assume dict or list
        if isinstance(prev_data, dict):
            vals = [v or CUSTOM_NULL for v in prev_data.values()]
        elif isinstance(prev_data, list):
            vals = prev_data
        for i, v in enumerate(vals):
            CARD_SUBLINES[i].append(v)
    elif attr == "?":
        if isinstance(prev_data, dict):
            vals = list(prev_data.keys())
        elif isinstance(prev_data, list):
            vals = [str(i) for i in range(0, len(prev_data))]
        for i, v in enumerate(vals):
            CARD_SUBLINES[i].append(v)
    elif attr == "/":
        # Resolve URL
        if prev_data.startswith("http"):
            new_data = get_uri_attribute(prev_data)
            # Switch to resolved URL data
            value = find_attrs(new_data, attributes[attr_level + 1 :], 0, [])
    elif attr == "spacer":
        # Special attribute for column spacing
        value = SPACER_MARKER
    else:
        drill_values.append(attr)  # No marker, assume property name
        if isinstance(attr_data(data, drill_values), (dict, list)):
            # End of attribute list, MUST resolve to a single value
            if attr_level == len(attributes) - 1:
                raise Exception(
                    "Endpoint is a dict/list : Need to use attribute markers!"
                )
            else:
                value = find_attrs(
                    data, attributes, attr_level + 1, drill_values
                )
                if value == None:
                    value = CUSTOM_NULL
        else:
            value = str(attr_data(data, drill_values))
            # keep going.. (might be URl to resolve)
            if attr_level != len(attributes) - 1:
                value = find_attrs(
                    data, attributes, attr_level + 1, drill_values
                )
                print(value)
    return value


def marker_replace(card: dict, match: re.Match) -> str:
    """Replace text following a replacement marker.

    Replacement marker is a %.
    Args:
        card: Card data
        match: RE match object for marker + text following it
    """
    raw_marker = str(match.group(0))  # May contain leading %s
    if raw_marker == "%":
        raise FormatError(f"Single '%' found in formatting string.")
    attr_marker_count = raw_marker.count("%") / 2

    # Leftover is actual attribute marker
    marker = raw_marker.replace("%%" * int(attr_marker_count), "")

    repl_str = "%" * int(attr_marker_count)
    if not attr_marker_count.is_integer():  # raw_marker has an attribute
        if marker in ATTR_CODES:
            marker = ATTR_CODES[marker]
        try:
            attrs = re.findall(r"%\{([^}]+)\}", marker)[0].split(
                ATTR_DELIM
            )  # %{attr}
        except Exception as e:
            raise FormatAttributeError(
                f"Could not find an attribute in {marker}!"
            ) from e
        repl_str += find_attrs(card, attrs, 0, [])
    else:  # raw_marker was all %s
        repl_str += marker
    return repl_str


def card_lines(card: dict, formatting: str) -> list[str]:
    """Return the printable line for a card.

    Note: Uses a global to track printing sublines

    Args:
        card: Card data (json dict)
        formatting: Formatting string

    Returns:
        List of printable lines
    """
    CARD_SUBLINES.clear()
    lines = [
        re.sub(
            r"%+(\{[^\}]+\}|.)", lambda x: marker_replace(card, x), formatting
        )
    ]
    if not lines[0].strip():  # If first line is empty, just print the sublines
        lines.clear()

    if CARD_SUBLINES:
        col_widths = [0] * len(list(CARD_SUBLINES.values())[0])
        for line_items in CARD_SUBLINES.values():
            for i, item in enumerate(line_items):
                col_widths[i] = max(col_widths[i], len(str(item)))
        for idx, line_items in CARD_SUBLINES.items():
            lines.append(
                " ".join(
                    [
                        f"{item:<{col_widths[c]}}"
                        for c, item in enumerate(line_items)
                    ]
                )
            )
    return lines
