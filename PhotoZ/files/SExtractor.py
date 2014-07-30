import os
import subprocess
from PhotoZ.files import functions


def make_catalogs(image_paths):
    # TODO: document
    # First, need to group the images based on what cluster they are of
    grouped_images = _group_images(image_paths)

    # We want to run everything on all the clusters, so iterate through them all
    for cluster in grouped_images:
        r_image, z_image = _find_r_and_z_images(cluster)

        # Test to make sure we have both r and z images
        # TODO: add a check for irac1 and 2 (if dual image mode is the way to go with those.)
        if not r_image and z_image:
            print "Both r and z images were not found for a cluster. Here are the paths for the images that were found:"
            for path in cluster:
                print path
        else:  # did find r and z images
            # Now we can do the SExtractor work on the r and z images
            pass









# TODO: do I need to make separate r-z function, or can I make a general SExtractor function?
def run_sextractor(detection_image, measurement_image):
    pass



def _group_images(image_paths):
    """Group images based on the cluster they are of.

    This is done by looking at the numbers in the filename of the image, which correspond to the coordinates of the
    image. Images with the same coordinate info should be grouped together.

    Specifically, this works by finding the string of coordinate digits, then making a dictionary with the
    coordinates as keys, and a list of images as values. As we go through the images, we can determine their
    coordinates, then put them in the proper list. At the end, one large list of lists is made from the values in the
    dictionary.

    :param image_paths: list of the locations of the images (using their full path).
    :return: list of lists, with image paths being grouped based on the cluster they contain
    """
    groups_dict = dict()
    for path in image_paths:
        filename = path.split("/")[-1]  # This takes the last thing, which will be the filename
        coordinates = _get_numbers_from_filename(filename)  # Calling then coordinates is generous, it is just an 8
        # digit string of digits that would make coordinates if parsed properly.
        if not coordinates in groups_dict:
            groups_dict[coordinates] = [path]
        else:
            groups_dict[coordinates].append(path)

    groups_list = groups_dict.values()

    return groups_list


def _get_numbers_from_filename(filename):
    """Parse the filename, and return the 8 digits that correspond to the coordinates of the image in the file.

    :param filename: filename to be parsed. Do not pass the full path, just the filename.
    :return: string of digits representing the coordinates from the filename.
    """
    coordinate_digits = ""
    for letter in filename:
        if len(coordinate_digits) < 8:  # Only the first 8 digits in the filename correspond to coordinates.
            if letter.isdigit():
                coordinate_digits += letter
    return coordinate_digits


def _find_r_and_z_images(images):
    # TODO: test,
    # TODO: document
    # Figure out which images are r and z TODO: add IRAC
    r_image, z_image = "", ""
    for image_path in images:
        band = functions.get_band_from_filename(image_path.split("/")[-1])  # the filename is after the last /
        if band == "r":
            r_image = image_path
        elif band == "z":
            z_image = image_path
        else:
            print "An image was passed in with a band I can't do anything with. Here is the path: " + image_path
        # TODO: put [3.6] and [4.5] in this when if I ever run things from IRAC images.
    return r_image, z_image


########################################################################################################################
# os.chdir(sextractor_params_directory)
# # TODO: use "which sex" to find the place SExtractor is. I use where mine is, but that may change.
# # TODO: after using "which sex", make it notice if SExtractor is not on the machine.
# subprocess.call(["/usr/local/scisoft///bin/sex", "/Users/gbbtz7/Astro/Data/gem/2013B/MOO0024+3303/MOO0024+3303_r.fits", "-c", "gmos.r.sex"])
########################################################################################################################