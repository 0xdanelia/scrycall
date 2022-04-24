import time


# shortcuts for printing card attributes in the format string
ATTR_CODES = {
    '%n': '%{name}',
    '%m': '%{mana_cost}',
    '%c': '%{cmc}',
    '%y': '%{type_line}',
    '%p': '%{power}',
    '%t': '%{toughness}',
    '%l': '%{loyalty}',
    '%o': '%{oracle_text}',
    '%f': '%{flavor_text}',
}


# TODO: refactor/add...
# printing columns with '%|'
# printing iterative values with '*' and '?'
# handling oracle text (or other values) that contain a line break
# traversing urls with '/'
def print_data(data_list, format_string):
    print_lines = []
    for data in data_list:
        print_line = get_print_line_from_data(data, format_string)
        print_lines.append(print_line)

    for line in print_lines:
        if line:
            print(line)


def get_print_line_from_data(data, format_string):
    print_line = format_string
    # to handle multiple percent characters next to one another, replace '%%' with a unique placeholder first
    percent_placeholder = '[PERCENT_' + str(time.time()) + ']'
    while percent_placeholder in print_line:
        percent_placeholder = '[PERCENT_' + str(time.time()) + ']'
    print_line = print_line.replace('%%', percent_placeholder)

    print_line = substitute_attributes_for_values(print_line, data)
    if print_line is None:
        return None

    # substitute the percent placeholder last
    print_line = print_line.replace(percent_placeholder, '%')
    return print_line


def substitute_attributes_for_values(print_line, data):
    # substitute the attribute shortcuts '%x' with their long form '%{attribute}' strings
    for attr_code in ATTR_CODES:
        print_line = print_line.replace(attr_code, ATTR_CODES[attr_code])

    while True:
        # replace any '%{attribute}' strings with the correct value from the input data
        attribute_name = get_next_attribute_name(print_line)
        if attribute_name is None:
            # get_next_attribute_name() returns None when there are no more attributes to substitute
            break
        attribute_value = get_attribute_value(attribute_name, data)
        # if any attribute value is None, do not print anything on this line
        if attribute_value is None:
            return None

        print_line = print_line.replace('%{' + attribute_name + '}', attribute_value)
    return print_line


def get_next_attribute_name(line):
    # attributes are formatted like '%{attribute_name}'
    start_idx = line.find('%{')
    if start_idx == -1 or start_idx == len(line) - 2:
        return None
    end_idx = line.find('}', start_idx)
    if end_idx == -1:
        return None
    attr = line[start_idx + 2: end_idx]
    return attr


def get_attribute_value(attribute_name, data):
    # nested attributes can be chained together like '%{top.middle.bottom}'
    nested_attributes = attribute_name.split('.')
    attr_value = data
    for attr in nested_attributes:
        attr_value = get_value_from_json_object(attr, attr_value)
        if attr_value is None:
            return None
    return attr_value


def get_value_from_json_object(attr, data):
    if isinstance(data, dict):
        return data.get(attr)
    elif attr.isdigit():
        # if the given data is not a dictionary, treat the data as a list and the attribute as the index
        idx = int(attr)
        if 0 <= idx < len(data):
            return data[idx]
    return None
