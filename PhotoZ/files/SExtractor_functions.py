def find_zeropoint(file_path):
    """

    :param file_path:
    :return:
    """
    sex_file = open(file_path, "r")
    lines = sex_file.readlines()
    for l in lines:
        if l.split():  # is not an empty list, so not a blank line either
            if l.split()[0] == "MAG_ZEROPOINT":
                return float(l.split()[1])