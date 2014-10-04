from PhotoZ.files import Cluster
import os
import re
import math
from matplotlib.backends.backend_pdf import PdfPages
import ezgal
import numpy as np


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

    # TODO: make the catalogs I was first given easily distinguishable from the other ones. I want them to be
    # different, so I can compare them to the ones my code makes from SExtractor.
    name = filename


    # First look for something of the form m####p####
    known_catalogs = re.compile("m[0-9]{4}(p|m)[0-9]{4}[.]phot[.]dat")
    # This means starts with an m, then 4 numeric characters, then p or m, then 4 more numeric characters

    my_catalog = re.compile(r"MOO[0-9]{4}([+]|[-])[0-9]{4}_(r|z)[.]cat")
    # This is the format my code outputs SExtractor catalogs with.

    gemini_images = re.compile(r"MOO[0-9]{4}([+]|[-])[0-9]{4}_(r|z)[.]fits")

    irac = re.compile(r"MOO_[0-9]{4}([+]|[-])[0-9]{4}_irac1_bg[.]fits[.]cat")
    # Format of IRAC catalogs. Has MOO_, 4 digits, + or -, 4 more digits, then _irac1_bg

    if my_catalog.match(name):
        return name[0:-6]  # Don't include band or extension
    elif gemini_images.match(name):
        return name[0:-7]  # Don't include band or extension
    elif irac.match(name):
        return "MOO" + name[4:13]  # MOO + the digits in the name
    elif known_catalogs.match(name):
        name = name[0:10]
        #  replace any p and m with + and - . I know I'm replacing the first m, but I will git rid of it next
        name = name.replace("p", "+")
        name = name.replace("m", "-")
        # Now have the beginning be taken off, and replaced with MOO.
        name = "MOO" + name[1:]

        # Create a dictionary mapping the objects to their known redshifts
        redshifts = {"MOO0012+1602": "0.94", "MOO0024+3303": "1.11", "MOO0125+1344": "1.12",
             "MOO0130+0922": "1.15", "MOO0133-1057": "0.96", "MOO0212-1813": "1.09", "MOO0224-0620": "0.81",
             "MOO0245+2018": "0.76", "MOO0319-0025": "1.19", "MOO1155+3901": "1.01", "MOO1210+3154": "1.05",
             "MOO1319+5519": "0.94", "MOO1335+3004": "0.98", "MOO1514+1346": "1.06", "MOO1625+2629": "1.20",
             "MOO2205-0917": "0.93", "MOO2320-0620": "0.92", "MOO2348+0846": "0.89", "MOO2355+1030": "1.27"}

        # Add the redshift to the name for easy access
        name += (", z = " + redshifts[name])
        return name



    print name
    # TODO: Test other things, like the format of the IRAC catalogs, as well as a general case for something that does
    #  not match. IF it doesn't match, tell the user that.
    # TODO: add cases for Gemini images, as well as IRAC images.
    return "not working"


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

def distance(x1, x2, y1, y2):
    """Uses the distance formula to calculate the distance between 2 objects
    dist = square root of the sum of the squared differences

    x and y are coordinates, so x1 and x2 are two values along one coordinate, and y1 and y2 are along the other.
    """
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def save_as_one_pdf(figs, filename):
    """
    Save the figures into one long PDF file

    :param figs: list of figures to be saved as PDFs
    :param filename: place where the PDFs will be saved
    :return: none
    """

    # Save the pdfs as one file
    pp = PdfPages(filename)
    for fig in figs:
        pp.savefig(fig)
    pp.close()

def make_prediction_dictionary(spacing):
    """
    Use the EzGal module to get model predictions, find correct slopes of RS, and turn this info into a dictionary
    where keys are redshifts, and values are objects storing all the data about the model prediction for that
    redshift

    :param spacing: float of how far apart the redshift predictions will be.
    :return: dictionary, where keys=redshifts and values=predictions object
    """

    # Make the models
    # For simplicity right now, just use the 0.1 gyr exponential model
    model = ezgal.ezgal("bc03_exp_0.1_z_0.02_chab_evolved_zf_3.0_ugrizch1ch2.model")
    #model = ezgal.ezgal("m05_ssp_z_0.02_krou_evolved_zf_3.0_ugrizch1ch2.model")

    # Set formation redshift and observed redshifts
    zf = 3.0
    zs = np.arange(0.5, 1.5000001, spacing)

    # Normalize to Dai et al 2009
    # model.set_normalization(filter='ch1', mag=-25.06, apparent=False, vega=True, z=0.24)
    # Normalize to Coma
    model.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

    # Calculate observables
    mags = model.get_apparent_mags(zf, filters=["sloan_r", "sloan_i", "sloan_z", "ch1", "ch2"], zs=zs, vega=False)
    # If the filters are changed, then the way the magnitudes are passed into the prediction object needs to be
    # changed as well. That work depends on the index of the specific filters
    # dimensions of mags: [redshifts, filters]

    # Now need to get slopes for all redshifts
    # The info here is stored in a file, so reading that will be all we need
    load_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/Best_fit_RS_slope.pickle")
    slope_dict = cPickle.load(load_file)
    # slope_dict is a dictionary of keys = redshifts, values = slopes
    load_file.close()

    # change redshifts to string format, so they don't get floating point errors
    zs = [str(round(z, 2)) for z in zs]

    # Initialize an empty dictionary
    predictions_dict = dict()

    for i in range(len(zs)):
        predictions_dict[zs[i]] = other_classes.Predictions(redshift=zs[i],
                                                            r_mag=mags[i][0],  # need to specify which filter
                                                            i_mag=mags[i][1],
                                                            z_mag=mags[i][2],
                                                            ch1_mag=mags[i][3],
                                                            ch2_mag=mags[i][4],
                                                            slope=slope_dict[float(zs[i])])
    return predictions_dict