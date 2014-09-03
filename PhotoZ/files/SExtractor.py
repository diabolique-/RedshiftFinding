import os
import subprocess
import matplotlib.pyplot as plt
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import SExtractor_functions
from PhotoZ.files import sdss_calibration
from PhotoZ.files import other_classes
from PhotoZ.files import catalog


def sextractor_main(image_paths):
    # TODO: document
    # First, need to group the images based on what cluster they are of
    grouped_images = _group_images(image_paths)
    # Have a list of tuples

    figures = []

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
                # Always use z as the detection image, since it is the reddest band in optical
                figure = _sextractor_process(z_image, measurement_image)


                # If it couldn't work (maybe there weren't any stars), exit.
                if not figure:
                    # TODO: ask Brodwin how to handle images that can't be calibrated to SDSS.

                    break  # skips else block

                else: # did work, and therefore returned a figure
                    figures.append(figure)
                # TODO: can also adjust FWHM from SExtractor catalog information



            else:  # no break in for loop (ie, calibration_success worked)

                pass
    # SAve all figures
    # TODO: integrate with file structure
    functions.save_as_one_pdf(figures, "/Users/gbbtz7/Desktop/calibration.pdf")

def _sextractor_process(detection_image, measurement_image):
    # TODO: document

    # Determine which .sex file to use
    if functions.get_band_from_filename(measurement_image) == "r":
        config_file = global_paths.r_config_file
    elif functions.get_band_from_filename(measurement_image) == "z":
        config_file = global_paths.z_config_file
    else:
        other_classes.EndProgramError("The SExtractor function for r and z bands was passed an image that isn't r "
                                      "or z. Something is wrong")


    # Get the default zeropoint from the file
    zero_point = SExtractor_functions.find_zeropoint(config_file)

    # Determine the name of the catalog
    sex_catalog_name = functions.make_cluster_name(measurement_image.split("/")[-1]) + ".cat"
    sex_catalog_path = global_paths.catalogs_save_directory + sex_catalog_name

    # Run SExtractor once before the loop, to get a baseline

    _run_sextractor(detection_image, measurement_image, config_file, str(zero_point), sex_catalog_path)

    # TODO: somewhere down the road, do aperture corrections. These are neccesary for calibrating
    #  optical to IR mags.

    # Read in the SExtractor catalog. We only want stars of a certain magnitude.
    # read the SExtractor catalog with my read_catalog_function. Pick out stars of a given mag range
    sex_stars = catalog.read_catalog(sex_catalog_path,
                                     desired_columns=["MAG_APER", "MAGERR_APER", "ALPHA_J2000", "DELTA_J2000"],
                                     label_type="m", label_row=0, data_start=8,
                                     filters=["FLAGS < 4", "MAGERR_APER < 0.2", "CLASS_STAR > 0.8", "MAG_APER > 17",
                                              "MAG_APER < ""20.5"])

    # Use the locations of these stars to make a corresponding SDSS catalog
    # TODO: ask Brodwin about how good this is. Is CLASS_STAR > 0.8 too constricting, or not constricting enough?

    # find the name of the SDSS catalog. catalogs path + name (derived from Sextractor catalog) + band_sdss.cat
    sdss_catalog_path = global_paths.calibration_catalogs_directory + sex_catalog_path.split("/")[-1].split("_")[0] + \
                                                                     "_sdss.cat"
    # See if the catalog exists, and if it doesn't, make it
    if not os.path.isfile(sdss_catalog_path):
        has_objects = sdss_calibration.make_sdss_catalog(sex_stars, sdss_catalog_path)
        # Check to see if there are actually objects in the catalog. If not, exit, since calibration won't work.
        if has_objects is False:
            # remove the SExtractor catalog, since it couldn't be calibrated properly
            os.remove(sex_catalog_path)
            return False


    # find the band of the SExtractor catalog, so we know what to calibrate
    band = functions.get_band_from_filename(sex_catalog_path.split("/")[-1])

    # Read the sdss catalog
    sdss_catalog = catalog.read_catalog(sdss_catalog_path, ["ra", "dec", band], label_type="s", label_row=0)

    # Each line is a source, so turn it into that.
    sdss_sources = [other_classes.Source(line[0], line[1], bands=[band], mags=[line[2]], mag_errors=[0])
                    for line in sdss_catalog]
    sex_sources = [other_classes.Source(line[2], line[3], bands=[band], mags=[line[0]], mag_errors=[line[1]])
                   for line in sex_stars]

    # Now find the best zero point for these sources
    # TODO: this might be minus
    zero_point_change = sdss_calibration.sdss_calibration(sex_sources, sdss_sources, band)
    # Check to see that the zero-point didn't return False.
    if zero_point_change is False:
        os.remove(sex_catalog_path)
        return False
    else:
        zero_point += zero_point_change
    # rerun SExtractor with this new calibrated zeropoint
    _run_sextractor(detection_image, measurement_image, config_file, str(zero_point), sex_catalog_path)
    # This should result in a calibrated catalog.


    # Ask the user if it is a good fit
    user_approved = False
    while not user_approved:
        # Read in new SExtractor catalog
        sex_stars = catalog.read_catalog(sex_catalog_path,
                                         desired_columns=["MAG_APER", "MAGERR_APER", "ALPHA_J2000", "DELTA_J2000"],
                                         label_type="m", label_row=0, data_start=8,
                                         filters=["FLAGS < 4", "MAGERR_APER < 0.2", "CLASS_STAR > 0.8", "MAG_APER > 17",
                                                  "MAG_APER < ""20.5"])
        # Turn them into sources
        sex_sources = [other_classes.Source(line[2], line[3], bands=[band], mags=[line[0]], mag_errors=[line[1]])
                       for line in sex_stars]

        # Match them with SDSS sources
        pairs = sdss_calibration.match_sources(sex_sources, sdss_sources)
        print len(pairs), "final pairs"

        # Initialize lists to be filled with data points
        sdss_mags, mag_differences, mag_errors = [], [], []

        for pair in pairs:
            # Calculate residuals
            pair[0].find_mag_residual(band, pair[1].mags[band].value)

            # Only want to plot ones with non-outlier residuals
            if abs(pair[0].mag_residuals[band].value) < 0.3:
                # Append things to the proper list
                sdss_mags.append(pair[1].mags[band].value)
                mag_differences.append(pair[0].mag_residuals[band].value)
                mag_errors.append(pair[0].mags[band].error)

        figure = plt.figure(figsize=(6, 5))
        ax = figure.add_subplot(1, 1, 1)

        ax.errorbar(sdss_mags, mag_differences, mag_errors, fmt=".", c="k")
        # TODO: add labels on axes
        return figure
        # user_input = raw_input("Does this look good? (y/n) ")
        # print user_input
        # if user_input == "Y" or "y":
        #     user_approved = True
        # else:
        #     user_approved = False

    # Now that it is done, return True to indicate that it worked.
            # TODO: do I really need this? Do I do anything with it?




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
