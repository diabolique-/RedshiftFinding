def find_zeropoint(file_path):
    """Finds the default zeropoint, as shown in the .sex config file.

    :param file_path: place where the .sex file is.
    :return: zeropoint specified in the file.
    """
    sex_file = open(file_path, "r")
    lines = sex_file.readlines()
    for l in lines:
        if l.split():  # is not an empty list, so not a blank line either
            if l.split()[0] == "MAG_ZEROPOINT":
                return float(l.split()[1])