import operator

class EndProgramError(Exception):
    """Exception class that ends the program when raised. Prints an error message,
    as well as optionally printing a value that caused the exception.
    """
    def __init__(self, message, offending_value=None):
        print message
        if offending_value:
            print "Here is the offending value: " + str(offending_value)
        raise SystemExit  # Exits the program

def _find_column_index(label_line, data_line, column_descriptor):
    # TODO: document.
    if type(column_descriptor) is str:  # It it's a string, it will be a label
        # Find the column corresponding to that label
        try:  # Want to catch errors if the desired element isn't a label
            return label_line.index(column_descriptor)
        except ValueError: # Thing isn't in the list
            raise EndProgramError("Error in read_catalog function. One of the column labels was not found among the labels of the file.", column_descriptor)
    elif type(column_descriptor) is int:  # If it's an integer, it will be a column number
        if len(data_line) * -1 <= column_descriptor < len(data_line):  # Want the column to actually be in the list
            # Negative indices are allowed
            return column_descriptor
        else:
            raise EndProgramError("Error in read_catalog function. One of the column numbers was not a valid index for the given file.", column_descriptor)
    else:
        raise EndProgramError("Error in read_catalog function. One of the desired columns was passed in as neither a string or an integer.", column_descriptor)

def _parse_filter_string(filter_string):
    filter_components = filter_string.split()

    # Make sure the final element has the right data type, since it will be compared to things of that type.
    filter_components[2] = _find_data_type(filter_components[2])

    # Now we can determine what the correct operator is
    if filter_components[1] == "==":
        filter_components[1] = operator.eq
    elif filter_components[1] == "!=":
        filter_components[1] = operator.ne
    elif filter_components[1] == "<":
        filter_components[1] = operator.lt
    elif filter_components[1] == ">":
        filter_components[1] = operator.gt
    elif filter_components[1] == "<=":
        filter_components[1] = operator.le
    elif filter_components[1] == ">=":
        filter_components[1] = operator.ge
    else:
        raise EndProgramError("Error in read_catalog function. Filter operator is not recognized.", filter_components[1])
    return filter_components





def _find_data_type(value):
    # TODO: document
    """returns the value, formatted to the correct data type."""
    if value.isdigit(): # All digits, so it is an integer
        return int(value)
    # Checking for floats is more complicated. IF there is one period,
    # and the entire rest of the string is digits, then it is a float
    elif value.count(".") == 1 and value.replace(".", "").isdigit():
        return float(value)
    # Return anything else as a string
    else:
        return str(value)

def read_catalog(filepath, desired_columns, label_row=None, data_start=None, separator=" ", filters=None):
    """ Find certain columns in a catalog text file. Can find columns based on
    either the labels for columns, or just their order.

    format params in PYCharm
    filepath: location of the file. Use the full path, not just the filename.
    desired_columns: list of desired columns to be returned. Elements can either
    be strings or integers. Strings should refer to labels of columns, as labeled
    on the line specified in the label_row parameter. Integers will refer to the
    position of the column. Remember Python indexing starts at 0!
    label_row: index of the row of the file that contains labels of the columns.
    If there are no labels, don't pass anything in.
    param data_start: index of the row of the file where the data starts. If
    nothing is passed in, it is assumed to be the line immediately after the label_row.
    param filtering: a string. Will be read.



    """

    # Open the file for reading
    try:
        f = open(filepath)
    except IOError:
        raise EndProgramError("Error in read_catalog function. The file to be opened was not found.")

    # Set the data line if the user hasn't already.
    if label_row == None and data_start == None:  # IF the user didn't say where labels are, assume there are none
        data_start = 0  # Since there is no label line, and the user didn't specify where the data starts, assume it is the first line.
    elif label_row != None and  data_start == None:  # If the labels are specified, but not where the data starts, it will be the first line after the labels
        data_start = label_row + 1

    # Read all lines in, strip them of whitespace, and split the lines.
    # This will make a list of lists, where each line is a sublist, and
    # the columns are elements of the smaller list
    if separator == " ":
        all_lines = [line.strip().split() for line in f.readlines()]
    else:
        all_lines = [line.strip().split(separator) for line in f.readlines()]

    # Also want the values to be in the right data type. If numbers are
    # involved, we don't want to pass strings back
    for row_idx in range(len(all_lines)):
        for item_idx in range(len(all_lines[row_idx])):
            # Now look at formatting of the item
            all_lines[row_idx][item_idx] = _find_data_type(all_lines[row_idx][item_idx])

    # Get rid of any # in the label line
    if all_lines[label_row][0] == "#":
        all_lines[label_row].remove("#")
    elif all_lines[label_row][0].startswith("#"):
        all_lines[label_row][0] = all_lines[label_row][0].replace("#", "")

    # find the columns the user wants
    column_idx_list = [_find_column_index(all_lines[label_row], all_lines[data_start], element) for element in desired_columns]

    if filters:
        filter_elements_list = [_parse_filter_string(f) for f in filters]
        filter_idx_list = [_find_column_index(all_lines[label_row], all_lines[data_start], f[0]) for f in filter_elements_list]

    table = []
    for l in range(len(all_lines)):
        if l >= data_start:
            line = all_lines[l]
            if filters:
                for f in range(len(filter_elements_list)):  # For all filters...
                    # ...test the condition. I tlooks funky since filter_elements[f][1] is a function! It will be a comparison operator (<, >, ==, etc).
                    # That comparison operator was assigned in the _parse_filter_string function.
                    if not filter_elements_list[f][1](line[filter_idx_list[f]], filter_elements_list[f][2]):
                        break  # It failed a filter test, and the break will skip the else clause, where we add this to the table.
                else: # No break, it passed all filter tests.
                    table.append([line[idx] for idx in column_idx_list])
            else:
                table.append([line[idx] for idx in column_idx_list])


    return table




cat1 = read_catalog("/Users/gbbtz7/Desktop/m1636p1019.sdss.cat", ["ra", "dec"], label_row=1, separator=",")
#print cat1
cat = read_catalog("/Users/gbbtz7/Desktop/m0012p1602.phot.dat", ["ra", "dec"], label_row=0, data_start=2)
#print cat
my_cat = read_catalog("/Users/gbbtz7/Desktop/sdss.cat", ["ra", "dec", "r", "z"], label_row=0, filters=["z > 20.0", "r < 22.0", "ra > 0.08", "dec < 0.05"]) #
print my_cat
