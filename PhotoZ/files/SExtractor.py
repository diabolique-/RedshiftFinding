import os
import subprocess
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import SExtractor_functions
from PhotoZ.files import sdss_calibration


def make_catalogs(image_paths):
    # TODO: document
    # First, need to group the images based on what cluster they are of
    grouped_images = _group_images(image_paths)
    # Have a list of tuples

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
            # Now we can do the SExtractor work oyn the r and z images
            for measurement_image in [z_image, r_image]:

                # Determine which .sex file to use
                if functions.get_band_from_filename(measurement_image) == "r":
                    config_file = global_paths.r_config_file
                elif functions.get_band_from_filename(measurement_image) == "z":
                    config_file = global_paths.z_config_file
                else:
                    print "The SExtractor function for r and z bands was passed an image that isn't r or z. " \
                          "Something is wrong"

                # Get the default zeropoint from the file
                zero_point = SExtractor_functions.find_zeropoint(config_file)

                # Determine the name of the catalog
                catalog_name = functions.make_cluster_name(measurement_image.split("/")[-1]) + ".cat"
                catalog_path = global_paths.catalogs_directory + catalog_name

                # Initialize other variables for the loop
                user_approved = False

                # Run SExtractor once before the loop, to get a baseline
                # Always use z as the detection image, since it is the reddest band in optical
                _run_sextractor(z_image, measurement_image, config_file, str(zero_point), catalog_path)

                # TODO: somewhere down the road, do aperture corrections. These are neccesary for calibrating
                #  optical to IR mags.

                calibration_success = sdss_calibration.sdss_calibration(catalog_path)
                # If it couldn't work (maybe there weren't any stars), exit.
                if calibration_success is False:
                    # TODO: ask Brodwin how to handle images that can't be calibrated to SDSS.

                    # remove the SExtractor catalog, since it couldn't be calibrated properly
                    os.remove(catalog_path)

                    break  # skips else block

                # Always use z as the detection image, since it is the reddest band in optical

                # TODO: can also adjust FWHM from SExtractor catalog information

                # _run_sextractor(z_image, measurement_image, config_file,str(zero_point), catalog_path)


            else:  # no break in for loop (ie, calibration_success worked)

                pass


# TODO: do I need to make separate r-z function, or can I make a general SExtractor function?

def _run_sextractor(detection_image, measurement_image, sex_file, zeropoint, catalog_path):
    # TODO: document
    os.chdir(global_paths.sextractor_params_directory)

    # TODO: Try to call "which sex" to determine where SExtractor is.
    sex = "/usr/local/scisoft///bin/sex"



    # Make sure we have r or z or both. Both images have to be r or z bands.
    if not ((functions.get_band_from_filename(detection_image) == "r" or
             functions.get_band_from_filename(detection_image) == "z") and
            (functions.get_band_from_filename(measurement_image) == "r" or
             functions.get_band_from_filename(measurement_image) == "z")):
        print "\n\n\n############################################################################################\n" \
              "The SExtractor function for r and z bands was passed an image that isn't r or z. \nSomething is " \
              "wrong.\n" \
              "############################################################################################\n\n\n"

        return



    # TODO: urgent: make a function to parse the filename into a catalog name.

    # Call SExtractor
    temp = subprocess.PIPE  # I don't want SExtractor's output to be seen, so create this to store it all.
    # subprocess.call puts things in command line (like terminal). Things have to be a list. It will put spaces
    # in between each item in the list when it actually does the command.
    subprocess.call([sex, detection_image, measurement_image, "-c", sex_file, "-CATALOG_NAME", catalog_path,
                     "-MAG_ZEROPOINT", zeropoint], stdout=temp)  # stdout is the pipe we just made, meaning that
                     # nothing is printed.



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
    # TODO: should this be here, or in the functions file?
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
