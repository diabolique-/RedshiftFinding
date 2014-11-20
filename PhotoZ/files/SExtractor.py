import os
import subprocess
import matplotlib.pyplot as plt
from astropy.io import fits
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import SExtractor_functions
from PhotoZ.files import sdss_calibration
from PhotoZ.files import other_classes
from PhotoZ.files import catalog


def sextractor_main(image_paths):
    """Perform the process to run SExtractor on a list of images.

    Matches r and z images, then calls the SExtractor function to run it with z as the detection image, and both r and z
    as measurement. Collects figures showing the calibration process, and then saves them.

    :param image_paths: list of strings that are the paths of all the images that will be run through SExtractor
    :type image_paths: list
    :return: None. Does make catalogs that are placed in the location the user specified in the global_paths file.
    """
    # First, need to group the images based on what cluster they are of
    grouped_images = _group_images(image_paths)
    # Will now have a list of tuples

    # Initialize list of figures to be filled as needed
    figures = []
    # We want to run everything on all the clusters, so iterate through them all
    for cluster in grouped_images:

        # Select the r and z band images in each pair. That is what will be used for now.
        r_image, z_image = _find_r_and_z_images(cluster)

        # Test to make sure we have both r and z images
        # TODO: add a check for irac1 and 2 (if dual image mode is the way to go with those.)
        if not (r_image and z_image):
            print "Both r and z images were not found for a cluster. Here are the paths for the images that were found:"
            for path in cluster:
                print path
        else:  # did find r and z images
            # Now we can do the SExtractor work on the r and z images
            for measurement_image in [z_image, r_image]:
                # Always use z as the detection image, since it is the reddest band in optical
                # TODO: DOCUMENTED TO HERE
                figure = _create_catalogs(z_image, measurement_image)
                # That function does the dirty work of running SExtractor and calibrating to SDSS. It returns a
                # figure object of the plot comparing the final SDSS calibration. If it couldn't work, it will return
                # False.


                # If it couldn't work (maybe there weren't any stars, etc),  exit.
                if not figure:
                    # TODO: ask Brodwin how to handle images that can't be calibrated to SDSS.

                    break  # skips else block

                else: # did work, and therefore returned a figure of the calibration process
                    figures.append(figure)
                # TODO: can also adjust FWHM from SExtractor catalog information

    # save the multipage pdf file
    functions.save_as_one_pdf(figures, global_paths.calibration_plots)
    # close all plots
    plt.close("all")


def _create_catalogs(detection_image, measurement_image):
    """Run the whole process of creating calibrated catalogs. Runs SExtractor, and then calibrates the catalog to SDSS.

    Does calibration by adjusting the zeropoint parameter in SExtractor.

    :param detection_image: path to the image that detection will be done in (generally z)
    :param measurement_image: path to the image that will be used as measurement. Can be any band.
    :return: figure showing the results of the SDSS calibration. Will be SDSS mags vs mag difference. Will return
    False if calibration failed for whatever reason (normally not enough sources matching between the image and the
    SDSS catalog.
    """
    # Determine which .sex file to use
    config_file = None # initialization to make PyCharm happy.
    if functions.get_band_from_filename(measurement_image) in ["r", "z"]:  # way to test both r and z bands at once
        config_file = global_paths.gemini_config_file
    else:
        other_classes.EndProgramError("The _create_catalogs function for r and z bands was passed an image that isn't r "
                                      "or z. Something is wrong", measurement_image)

    # Get the default zeropoint from the file
    zero_point = SExtractor_functions.find_zeropoint(config_file)

    # find the FWHM
    fwhm = get_fwhm(measurement_image)

    # TODO: get the FWHM (probably from SExtractor) if the FWHM isn't in the image header.


    # Determine the name of the catalog. Will be of the form Filename_band.cat
    sex_catalog_name = functions.make_cluster_name(measurement_image.split("/")[-1]) + "_" +\
                       functions.get_band_from_filename(measurement_image) + ".cat"
    # add the directory the catalog should be stored in.
    sex_catalog_path = global_paths.catalogs_save_directory + sex_catalog_name

    # Run SExtractor once before the calibration loop, to get a baseline before calibration
    _run_sextractor(detection_image, measurement_image, config_file, str(zero_point), fwhm, sex_catalog_path)

    # TODO: somewhere down the road, do aperture corrections. These are neccesary for calibrating
    #  optical to IR mags.

    # Read in the SExtractor catalog. We only want stars of a certain magnitude for good calibration.
    sex_stars = catalog.read_catalog(sex_catalog_path,
                                     desired_columns=["MAG_APER", "MAGERR_APER", "ALPHA_J2000", "DELTA_J2000"],
                                     label_type="m", label_row=0, data_start=8,
                                     filters=["FLAGS < 4", "MAGERR_APER < 0.2", "CLASS_STAR > 0.8", "MAG_APER > 17",
                                              "MAG_APER < 20.5"])


    # Use the locations of these stars to make a corresponding SDSS catalog
    # TODO: ask Brodwin about how good this is. Is CLASS_STAR > 0.8 too constricting, or not constricting enough?

    # make the name of the SDSS catalog. catalogs path + name (derived from Sextractor catalog) + band_sdss.cat
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
    sdss_catalog = catalog.read_catalog(sdss_catalog_path, ["ra", "dec", band], label_type="s", label_row=1)

    # Each line is a source, so turn both the SExtractor and SDSS catalogs into source objects
    # TODO: CHECK THAT THESE ARE THE RIGHT COLUMNS TO READ IN
    sdss_sources = [other_classes.Source(line[0], line[1], mag_bands=[band], mags=[line[2]], mag_errors=[0])
                    for line in sdss_catalog]
    sex_sources = [other_classes.Source(line[2], line[3], mag_bands=[band], mags=[line[0]], mag_errors=[line[1]])
                   for line in sex_stars]

    # Now find the best zero point for these sources
    zero_point_change = sdss_calibration.sdss_calibration(sex_sources, sdss_sources, band)
    # Check to see that the zero-point didn't return False.
    if zero_point_change is False:
        # If calibration didn't work, get rid of the catalog, and exit the SExtractor function
        os.remove(sex_catalog_path)
        return False
    else:  # calibration did work, so change the zero point to the calibrated value
        zero_point += zero_point_change


    # rerun SExtractor with this new calibrated zeropoint
    _run_sextractor(detection_image, measurement_image, config_file, str(zero_point), fwhm, sex_catalog_path)
    # This should result in a calibrated catalog.

    # We want user input on whether the calibration is good or not. Showing a plot will be the best way
    while True:  # Will return to get out of the function once it is good enough for the user
        # Read in new SExtractor catalog
        sex_stars = catalog.read_catalog(sex_catalog_path,
                                         desired_columns=["MAG_APER", "MAGERR_APER", "ALPHA_J2000", "DELTA_J2000"],
                                         label_type="m", label_row=0, data_start=8,
                                         filters=["FLAGS < 4", "MAGERR_APER < 0.2", "CLASS_STAR > 0.8", "MAG_APER > 17",
                                                  "MAG_APER < 20.5"])
        # Turn them into sources
        sex_sources = [other_classes.Source(line[2], line[3], mag_bands=[band], mags=[line[0]], mag_errors=[line[1]])
                       for line in sex_stars]

        # Match them with SDSS sources
        pairs = []
        for source in sex_sources:
            match = sdss_calibration.find_match(source, sdss_sources)
            if match:
                pairs.append((source, match))
        if len(pairs) == 0:
            # remove the SExtractor catalog, since it couldn't be calibrated properly
            print functions.make_cluster_name(sex_catalog_path.split("/")[-1]) + " could not be calibrated properly. No sources matched SDSS sources."
            os.remove(sex_catalog_path)
            return False  # calibration didn't work
        # Initialize lists to be filled with data points
        sdss_mags, mag_differences, mag_errors = [], [], []

        for pair in pairs:
            # Calculate residuals
            pair[0].find_mag_residual(band, pair[1].mags[band].value)

            # Only want to plot ones with non-outlier residuals
            # if abs(pair[0].mag_residuals[band].value) < 1.0:
                # Append things to the proper list
            sdss_mags.append(pair[1].mags[band].value)
            mag_differences.append(pair[0].mag_residuals[band].value)
            mag_errors.append(pair[0].mags[band].error)

        # create figure and axis
        figure = plt.figure(figsize=(6, 5))
        ax = figure.add_subplot(1, 1, 1)

        # If all the points were outliers, then they will not be appended. I'm not sure this should ever happen, though.
        if len(sdss_mags) == 0 or len(mag_differences) == 0 or len(mag_errors) == 0:
            # remove the SExtractor catalog, since it couldn't be calibrated properly
            os.remove(sex_catalog_path)
            print functions.make_cluster_name(sex_catalog_path.split("/")[-1]) + " could not be calibrated properly. " \
                                                                                "No " \
                                                                             "sources " \
                                                                   "matched SDSS " \
                                                   "sources. This is the " \
                                    "second time, though, so something is probably wrong."
            return False

        ax.errorbar(sdss_mags, mag_differences, mag_errors, fmt=".", c="k")
        ax.set_xlabel("SDSS mag")
        ax.set_ylabel("SDSS - measured mags")
        ax.set_title(sex_catalog_name[:-4])
        # plt.show()
        #
        # user_input = raw_input("Does this look good? (y/n) ")
        # if user_input == "Y" or "y":
        #     return figure
        # else:
        #     zero_point_change = raw_input("Where is the current best fit line?")
        #     zero_point += zero_point_change
        #     # rerun SExtractor with new zeropoint adjustment
        #     _run_sextractor(detection_image, measurement_image, config_file, str(zero_point), sex_catalog_path)
        return figure




# TODO: do I need to make separate r-z function, or can I make a general SExtractor function?

def _run_sextractor(detection_image, measurement_image, sex_file, zeropoint, fwhm, catalog_path):
    """Run SExtractor from the command line on the given images.

    Runs in dual image mode. If single image mode is wanted, set both as the same. The .sex configuration file needs
    to be specified. The zeropoint can be changed, as well as the path the resulting catalog will be saved to.

    :param detection_image: path of the detection image
    :type detection_image: str
    :param measurement_image: path of the measurement image (can be the same as the detection image)
    :type measurement_image: str
    :param sex_file: path to the .sex configuration file for SExtractor
    :type sex_file: str
    :param zeropoint: zeropoint for SExtractor magnitudes.
    :type zeropoint: str
    :param fwhm: full width half max of the image.
    :type fwhm: str
    :param catalog_path: path where the resulting SExtractor catalog will be stored.
    :type catalog_path: str
    :return: None, but the resulting catalog is saved to disk (by SExtractor)
    """
    os.chdir(global_paths.sextractor_params_directory)

    # TODO: Try to call "which sex" to determine where SExtractor is.
    sex = "/usr/local/scisoft///bin/sex"

    # Make sure we have r or z or both. Both images have to be r or z bands.
    if not ((functions.get_band_from_filename(detection_image) == "r" or
             functions.get_band_from_filename(detection_image) == "z") and
            (functions.get_band_from_filename(measurement_image) == "r" or
             functions.get_band_from_filename(measurement_image) == "z")):

        other_classes.EndProgramError("The SExtractor function for r and z bands was passed an image that isn't r or z. "
                                      "\nSomething is wrong.\n")

    # Call SExtractor
    temp = subprocess.PIPE  # I don't want SExtractor's output to be seen, so create this to store it all.
    # subprocess.call puts things in command line (like terminal). Things have to be a list. It will put spaces
    # in between each item in the list when it actually does the command.
    subprocess.call([sex, detection_image, measurement_image, "-c", sex_file, "-CATALOG_NAME", catalog_path,
                     "-MAG_ZEROPOINT", zeropoint, "-SEEING_FWHM", fwhm], stdout=temp)  # stdout is the pipe we just
                     # made, meaning that nothing is printed.



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
        if not coordinates in groups_dict:  # If the cluster isn't already in the dict, make it be
            groups_dict[coordinates] = [path]
        else:  # If it's already there, add the current image to the list of images.
            groups_dict[coordinates].append(path)

    groups_list = groups_dict.values()  # keys are the "coordinates", which we don't care about

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
    # DOCUMENTED
    """Take a list of images paths of images of one cluster, and figures out which is r, and which is z.

    :type images: list of strings showing the file paths for the images.
    :return: path for r image, path for z image.
    """
    # TODO: is this the best way to go? I will need to work with arbitrary bands at some point in the future.

    r_image, z_image = "", ""  # To make PyCharm happy (says I might return something that hasn't been assigned.

    for image_path in images:
        band = functions.get_band_from_filename(image_path.split("/")[-1])  # the filename is after the last /
        if band == "r":
            r_image = image_path
        elif band == "z":
            z_image = image_path
        else:
            print("An image was passed in in a band that I don't know how to handle now:" + image_path)
    return r_image, z_image

def get_fwhm(image_path):
    #TODO: document
    fits_file = fits.open(image_path)
    try:
        fwhm = str(fits_file[0].header["FWHMPSF"])
    except KeyError:
        print image_path.split("/")[-1] + " does not have a FWHM in the .fits header. FWHM set at ~0.7 arcseconds."
        # Get the FWHM from somewhere else
        # Don't know where to get it from at the moment, so I'll pick something that would be bad seeing. I'll also
        # make it something that can be identified easily, so I can identify it later to potentially replace it.
        fwhm = "0.7110011001100110011001100"
    fits_file.close()
    return fwhm