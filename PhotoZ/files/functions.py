import os

def find_all_objects(enclosing_directory, extension, files_list):
    """Recursively search the specified directory (and its subdirectories) for files that end in the desired extension.

    :param enclosing_directory: highest level directory containing the files
    :param extension: extension that the files returned will end with
    :param files_list: list that the desired files will be appended to.
    :return: files_list, with the paths of all the files appended to it
    """

    # Make sure enclosing directory has a finishing /
    if not enclosing_directory.endswith("/"):
        enclosing_directory += "/"

    for f in os.listdir(enclosing_directory):
        # Determine if the item is a directory or not
        entire_path = enclosing_directory + f
        if os.path.isdir(entire_path):
            # If it is a diretory, search through that directory with this function.
            find_all_objects(entire_path, extension, files_list)
            # We don't need to record the output of the function, since the list we pass in will be modified in place.
        else:
            if entire_path.endswith(extension):
                files_list.append(entire_path)

    return files_list
    # We technically don't need to return files_list, since changes in it will be reflected in the main program,
    # but often the user will just pass in2 an empty list without assigning it first. In this case, we need to return
    # something.

# def SExtractor(image_pat
# TODO: write this function
# Make sure that it does SExtractor on the images, with the correct parameters (including saving them to the right
# place), calibration, and correct naming conventions for the file (has to contain the band in the spot that
# read_sextractor_catalogs will look. I want each image to have its own SExtrator .sex file, for easier adjustments
# of zero point. Although I'm not sure
# TODO: think about whether I want each cluster to have its own .sex file or not.

# TODO: make a function to do calibrations (Sloan, whatever IRAC needs)

def read_sextractor_catalogs(catalogs_directory):
    # TODO: document
    for f in os.listdir(catalogs_directory):
        if f.endswith(".cat"):  # Need to only use files that are actually catalogs.
            catalog = open(catalogs_directory + f, "r")
            # Read all lines in, breaking them apart into their columns as we go.
            catalog_lines = [line.split() for line in catalog.readlines()]
            # catalog_lines is now a list of lists of strings. Each interior list is a line.
            catalog.close()  #We are done with the file, since we read everything in.

            # Determine what band the image is in, based on its filename.
            band = f.split(".")[-2]  # if the file is in the format name.band.cat, the second to last string between
            # the periods is the band.

            # Now use the header lines to determine what is in each column of the catalog
            for line in catalog_lines:
                if line[0] == "#":  # The commented lines at the top are the ones we want.
                    if line[2] == "ALPHA_J2000":  # RA
                        ra_index = int(line[1]) - 1
                        # We have to subtract one since Python indexing starts at 0, while SExtractor starts at 1
                    elif line[2] == "DELTA_J2000": # dec
                        dec_index = int(line[1]) - 1
                    elif line[2].startswith("MAG_"): # magnitude
                        # Used .startswith, since there are multiple magnitude options in SExtractor. the _ is to
                        # distinguish this line from MAGERR
                        mag_index = int(line[1]) - 1
                    elif line[2].startswith("MAGERR"): # magnitude error
                        mag_err_index = int(line[1]) - 1
                    elif line[2] == "FLAGS":
                        flags_index = int(line[1]) - 1
                    elif line[2] == "CLASS_STAR":  # How star-like the source is
                        class_star_index = int(line[1]) - 1
                    


            # TODO: store the data in the source objects if they already exist, otherwise make a new one. Need to
            # match them somehow to ones

            pass
