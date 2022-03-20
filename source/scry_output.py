import time
from enum import Enum
from typing import Optional, Union
import re
import string

from scry_data import get_uri_attribute_from_url


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
}
ATTR_DELIM = "."
CUSTOM_NULL = None


def print_cards(cards: list[str], formatting: str) -> None:
    """Print each card line-by-line

    Args:
        cards: _description_
        formatting (_type_): _description_
    """
    lines = []
    for card in cards:
        for line in card_lines(card, formatting):
            lines.append(line)
            # # separate newline characters
            # newline_cols = []
            # most_newlines = 0
            # for col in line:
            #     split_col = col.split("\n")
            #     most_newlines = max(most_newlines, len(split_col))
            #     newline_cols.append(split_col)

            # # fill the shortest column with whitespace so they are all the same size
            # for newline_col in newline_cols:
            #     while len(newline_col) < most_newlines:
            #         newline_col.append("")

            # # separate each line to be printed one at a time
            # for i in range(len(newline_cols[0])):
            #     line = []
            #     for newline_col in newline_cols:
            #         line.append(newline_col[i])
            #     lines.append(line)

    for line in lines:
        print(line)

    # # calculate column widths
    # num_cols = len(lines[0])
    # col_widths = [0] * num_cols
    # for row in lines:
    #     for w in range(num_cols):
    #         col_widths[w] = max(len(row[w]), col_widths[w])

    # # print the data
    # for column_list in lines:
    #     print_line = ""
    #     for i in range(num_cols):
    #         print_line = print_line + "{: <" + str(col_widths[i]) + "}"
    #     print_line = print_line.format(*column_list)
    #     print(print_line.replace("\n", " ").rstrip(" "))


def attr_data(data: dict, attributes: list[Union[str, int]]):
    """Get data from a data structure, drilling down."""
    rval = data
    for attr in attributes:
        print(f"rval attr: {attr}")
        rval = rval[attr]
    return rval


def find_attrs(
    data: dict, attributes: list[str], attr_level: int, drill_values: list
) -> str:
    """Find the given attribute(s) within the given data

    Attribute Markers:
        ? = Available property names
        * = Iterate properties
        ^ = Print previous property

    Args:
        card: data
        attributes: List of attributes or attribute markers

    Returns:
        Attribute or ERR
    """
    value = ""
    attr = attributes[attr_level]
    prev_data = attr_data(data, drill_values)
    print(f"attr: {attr}")
    if attr == "*":
        # Assume dict or list
        print(str(type(prev_data)))
        print(prev_data)
        if isinstance(prev_data, dict):
            value = ",".join([v or CUSTOM_NULL for v in prev_data.values()])
        elif isinstance(prev_data, list):
            value = ",".join(prev_data)
    elif attr == "?":
        if isinstance(prev_data, dict):
            value = ",".join(list(prev_data.keys()))
        elif isinstance(prev_data, list):
            value = ",".join([str(i) for i in range(0, len(prev_data))])
    # If the previous value is a url,  query it
    elif attr == "/":
        value = get_uri_attribute_from_url(value)
    else:
        if isinstance(data[attr], (dict, list)):
            if (
                attr_level == len(attributes) - 1
            ):  # End of attribute list, MUST resolve to a single value
                raise Exception(
                    "Endpoint is a dict/list : Need to use attribute markers!"
                )
            else:
                drill_values.append(attr)
                value = find_attrs(
                    data, attributes, attr_level + 1, drill_values
                )
                if value == None:
                    value = CUSTOM_NULL
        else:
            value = data[attr]
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
        print(attrs)
        repl_str += find_attrs(card, attrs, 0, [])
    else:  # raw_marker was all %s
        repl_str += marker
    return repl_str


def card_lines(card: dict, formatting: str) -> list[str]:
    """Return the printable line for a card.

    Args:
        card: Card data (json dict)
        formatting: Formatting string

    Returns:
        List of printable lines
    """
    # Initialize output line
    print(f"{formatting}")

    return [re.sub(r"%+[^%\s]*", lambda x: marker_replace(card, x), formatting)]


#
def get_available_attr_names(data) -> Optional[list]:
    """Get all names that could be used to iterate an attribute

    If the attribute is a dictionary, return the keys
    if it is a list or string, return the list of valid indexes

    Args:
        data: data

    Returns:
        List of available attribute names or None
    """
    if type(data) is dict:
        return list(data)
    if type(data) is list or type(data) is str:
        return list(range(len(data)))
    return None
