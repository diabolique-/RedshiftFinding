from PhotoZ.files import Cluster
import os
import re

# TODO: make read catalogs function, should work for both SExtractor and SDSS


def find_all_objects(enclosing_directory, extensions, files_list):
    """Recursively search the specified directory (and its subdirectories) for files that end in the desired extension.

    :param enclosing_directory: highest level directory containing the files
    :param extensions: List of possible extensions to be found.
    :type extensions: list of str
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
            find_all_objects(entire_path, extensions, files_list)
            # We don't need to record the output of the function, since the list we pass in will be modified in place.
        else:
            for ext in extensions:
                if entire_path.endswith(ext):
                    files_list.append(entire_path)

    return files_list
    # We technically don't need to return files_list, since changes in it will be reflected in the main program,
    # but often the user will just pass in2 an empty list without assigning it first. In this case, we need to return
    # something.


# Make sure that it does SExtractor on the images, with the correct parameters (including saving them to the right
# place), calibration, and correct naming conventions for the file (has to contain the band in the spot that
# read_sextractor_catalogs will look. I want each image to have its own SExtrator .sex file, for easier adjustments
# of zero point. Although I'm not sure
# TODO: think about whether I want each cluster to have its own .sex file or not.

# TODO: make a function to do calibrations (Sloan, whatever IRAC needs)


def _determine_which_cluster(clusters_list, catalog_name):
    # TODO: document once I can verify that this works.
    name = make_cluster_name(catalog_name)

    for c in clusters_list:
        if c.name == name:
            return c

    # Since we got this far, we know it's not in the list. We now initialize a new cluster object with empty
    clusters_list.append(Cluster.Cluster(name, []))
    return clusters_list[-1]
    #TODO: Verify that this works! I'm pretty sure it will, but not 100%.
    # May need to do this instead.
    # # Now can check again.
    # for c in clusters_list:
    #     if c.name == name:
    #         return c


def make_cluster_name(filename):
    """Find the name of a cluster, based on its filename.

    Uses regular expressions to parse filenames, so I included lots of comments to try and explain what I'm doing here.

    :param filename: Filename that will be parsed into a cluster name.
    :type filename: str
    :return: name of the cluster
    :rtype: str
    """
    name = filename.split(".")[0]

    # First look for something of the form m####p####
    simplest = re.compile("m[0-9]{4}p|m[0-9]{4}")
    # This means starts with an m, then 4 numeric characters, then p or m, then 4 more numeric characters

    # Look for format of Gemini images
    gemini_image = re.compile("MOO[0-9]{4}\+|\-[0-9]{4}_r|z\.fits")
    # MOO, then 4 numeric characters, then + or -, then 4 numeric characters, then _, then r or z, then .fits
    # This is the format my code outputs SExtractor catalogs with. TODO: is it? Should probably use IRAC catalog format

    if simplest.match(name):
        # First replace any p and m with + and - . I know I'm replacing the first m, but I will git rid of it next
        name = name.replace("p", "+")
        name = name.replace("m", "-")
        # Now have the beginning be taken off, and replaced with MOO
        name = "MOO" + name[1:]
        return name

    elif gemini_image.match(name):
        return name  # name is good as is

    # TODO: Test other things, like the format of the IRAC catalogs, as well as a general case for something that does
    #  not match. IF it doesn't match, tell the user that.
    # TODO: add cases for Gemini images, as well as IRAC images.
    return name


def check_for_slash(path):
    """Check the given directory for a slash at the end. If it doesn't have one, add it.

    :param path: Path to be checked for a slash.
    :type path: str
    :return: corrected path
    :rtype: str
    """
    if path.endswith("/"):
        return path
    else:
        return path + "/"


def get_band_from_filename(filename):
    """Finds the band of an image or catalog based on the filename.

    Assumes file names are of the form object_name_band.extension

    :param filename: string with the filename
    :return: string containing the band
    """
    file_no_extension = filename.split(".")[0]  # first thing before a .
    band = file_no_extension.split("_")[-1]  # the band will be the last thing in the name itself
    return band