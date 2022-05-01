import time

from scry_data import get_json_data_from_url


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


def print_data(data_list, format_string):
    # to handle multiple percent characters next to one another, replace '%%' with a unique placeholder first
    while True:
        percent_placeholder = '[PERCENT_' + str(time.time()) + ']'
        if percent_placeholder not in format_string:
            break
    format_string = format_string.replace('%%', percent_placeholder)

    # rather than split the format_string into separate columns now, do it after the data is substituted
    while True:
        column_placeholder = '[COLUMN_' + str(time.time()) + ']'
        if column_placeholder not in format_string:
            break
    format_string = format_string.replace('%|', column_placeholder)

    print_lines = []
    for data in data_list:
        print_lines += get_print_lines_from_data(data, format_string, percent_placeholder, column_placeholder)

    if not print_lines:
        return

    # at this point, print_lines is a 2D list of rows and columns
    num_columns = len(print_lines[0])
    column_widths = [0] * num_columns
    # cycle through the data to find out how wide each column needs to be
    for row in print_lines:
        for i in range(num_columns):
            column_widths[i] = max(column_widths[i], len(row[i]))

    # pad each column with whitespace and concat them together to print a row
    for row in print_lines:
        padded_row = ''
        for i in range(num_columns):
            padded_column = row[i].ljust(column_widths[i])
            padded_row += padded_column
        print(padded_row.rstrip())


def get_print_lines_from_data(data, format_string, percent_placeholder, column_placeholder):
    print_line = format_string

    print_lines = substitute_attributes_for_values(print_line, data)
    if not print_lines:
        return []

    # substitute the percent placeholder in each print_line
    for i in range(len(print_lines)):
        print_lines[i] = print_lines[i].replace(percent_placeholder, '%')

    # turn each print_line into a list, where each element is one column to be printed
    column_lines = []
    for line in print_lines:
        line_columns = line.split(column_placeholder)
        # line_columns is currently one row divided into columns
        # we want each newline within those columns to become its own row
        newline_rows_by_columns = preserve_newlines_in_columns(line_columns)
        for newline_row in newline_rows_by_columns:
            column_lines.append(newline_row)

    return column_lines


def substitute_attributes_for_values(print_line, data):
    # substitute the attribute shortcuts '%x' with their long form '%{attribute}' strings
    for attr_code in ATTR_CODES:
        print_line = print_line.replace(attr_code, ATTR_CODES[attr_code])

    print_lines = []

    while True:
        # replace any '%{attribute}' strings with the correct value from the input data
        attribute_name = get_next_attribute_name(print_line)
        if attribute_name is None:
            # get_next_attribute_name() returns None when there are no more attributes to substitute
            break

        if '*' in attribute_name:
            # '*' in an attribute can generate multiple lines
            iterated_print_lines = iterate_attributes_in_print_line(print_line, attribute_name, data)
            for line in iterated_print_lines:
                print_lines += substitute_attributes_for_values(line, data)
            return print_lines

        else:
            attribute_value = get_attribute_value(attribute_name, data)
            # if any attribute value is None, do not print anything on this line
            if attribute_value is None:
                return []
            print_line = print_line.replace('%{' + attribute_name + '}', str(attribute_value))

    # even if only one line is printed, return it in a list so that it can be iterated in earlier functions
    print_lines.append(print_line)

    return print_lines


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
    prev_attr_name = None
    for attr in nested_attributes:
        if attr == '?':
            # return a list of the currently valid attribute names
            attr_value = get_list_of_available_attribute_names(attr_value)
        elif attr == '^':
            # return the name of the previous attribute
            attr_value = prev_attr_name
        elif attr == '/':
            # if the previous value is a scryfall api endpoint, return its data
            if isinstance(attr_value, str) and attr_value.startswith('https://api.scryfall.com/'):
                attr_value = get_json_data_from_url(attr_value)
            else:
                return None
        else:
            attr_value = get_value_from_json_object(attr, attr_value)
        if attr_value is None:
            return None
        prev_attr_name = attr
    return attr_value


def get_list_of_available_attribute_names(data):
    if isinstance(data, dict):
        return list(data.keys())
    elif isinstance(data, list):
        return range(len(data))
    else:
        return range(len(str(data)))


def get_value_from_json_object(attr, data):
    if isinstance(data, dict):
        return data.get(attr)
    elif attr.isdigit():
        # if the given data is not a dictionary: treat the data as iterable, and treat the attribute as the index
        if isinstance(data, list):
            iterable_data = data
        else:
            iterable_data = str(data)
        idx = int(attr)
        if 0 <= idx < len(iterable_data):
            return iterable_data[idx]
    return None


def iterate_attributes_in_print_line(print_line, attribute_name, data):
    # for each possible value that '*' produces for a given attribute,
    # create a new print_line, replacing the '*' with each possible individual value.

    if attribute_name.startswith('*'):
        star_idx = -1
        sub_attr_value = data
        attr_to_replace = '*'
    else:
        star_idx = attribute_name.find('.*')
        sub_attr_name = attribute_name[:star_idx]
        sub_attr_value = get_attribute_value(sub_attr_name, data)
        attr_to_replace = sub_attr_name + '.*'

    iterated_lines = []
    values_to_iterate = get_list_of_available_attribute_names(sub_attr_value)

    for iterated_value in values_to_iterate:
        new_sub_attr_name = attr_to_replace.replace('*', str(iterated_value))
        # if the print_line contains duplicate sub-attributes, all will be replaced here
        new_print_line = print_line.replace('%{' + attr_to_replace, '%{' + new_sub_attr_name)

        if '*' in attribute_name[star_idx + 2:]:
            # multiple stars in a single attribute are handled recursively
            new_attribute_name = attribute_name.replace(attr_to_replace, new_sub_attr_name, 1)
            iterated_lines += iterate_attributes_in_print_line(new_print_line, new_attribute_name, data)
        else:
            iterated_lines.append(new_print_line)

    return iterated_lines


def preserve_newlines_in_columns(cols):
    # given a list where each element is a single column,
    # return a 2D list where each column is preserved, but each newline gets its own row
    num_cols = len(cols)
    output_cols = []
    for i in range(num_cols):
        output_cols.append([])
    max_rows = 0

    for i in range(num_cols):
        split_column = cols[i].split('\n')
        max_rows = max(max_rows, len(split_column))
        for col_row in split_column:
            output_cols[i].append(col_row)

    # insert empty strings into the shorter columns so that the output is consistent
    for i in range(num_cols):
        while len(output_cols[i]) < max_rows:
            output_cols[i].append('')

    output_rows = []
    # earlier functions expect each element of the output to be a row, rather than a column
    for i in range(max_rows):
        row = []
        for col in output_cols:
            row.append(col[i])
        output_rows.append(row)

    return output_rows
