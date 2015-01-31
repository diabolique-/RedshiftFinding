import cPickle
import math
import random
import os

from matplotlib.backends.backend_pdf import PdfPages
import ezgal
import numpy as np

from UselessNow.NotFromImages import other_classes


def read_cluster_objects(file_path="/Users/gbbtz7/GoogleDrive/Research/Data/PythonSavedClusters"):

    """Turn pickled objects in a directory to a list of unpickled objects

    :param file_path: Place where the pickled objects are stored.
    :type file_path: str
    :return: list of pickled objects from the directory.
    """

    cluster_list = []
    for c in os.listdir(file_path):
        if c.endswith(".p"):  # Only want pickle objects
            cluster_list.append(cPickle.load(open(file_path + "/" + c, "r")))

    return cluster_list


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


def calculate_sigma(galaxy, model_color):
    """Calculate how many sigma the given galaxy is from the model. Includes the RS scatter.

    :param galaxy: Galaxy object we will calculate the sigma for
    :param model_color: Color predicted by the model for the galaxy, given its magnitude.
    :return: How many sigma the galaxy is away from the model.
    """
    # Calculate errors in quadrature: error = sqrt(error1**1 + error2**2)
    error = math.sqrt(galaxy.color_error**2 + 0.05**2)  # 0.05 is intrinsic spread of red sequence
    return abs(model_color - galaxy.color) / error


def simple_chi_square(galaxies, model_line):
    """Does a simple reduced chi-square fit for a list of galaxies to a model line.

    Doesn't do any filtering. All galaxies passed in will be used. If any filtering of the galaxies is needed, do that
    outside this function.

    :param galaxies: List of galaxies to be included in the fit
    :param model_line: Line object holding data that represents the model's predictions we are fitting to
    :return: reduced chi-squared value
    """
    # Initialize some placeholders
    chi_sq = 0
    for gal in galaxies:
        # find color model predictions for the galaxy at the given magnitude
        idx = model_line.xs.index(gal.mag)
        chi_sq += ((model_line.ys[idx] - gal.color) / gal.color_error)**2
    # Reduced chi squared takes the total chi squared value and divides by degrees of freedom.
    # Degrees of freedom = number of data points - number of parameters (redshift, in this case) - 1
    return chi_sq / (len(galaxies) - 1 - 1)


def sample_with_replacement(data, sample_length):
    """Creates a reandom sample with replacement, for use with bootstrapping.

    :param data: List of data points
    :param sample_length: length of desired sample
    :return: new sample, with random sampling with replacement
    """
    # Pick the desired number of random data points. Data points can be selected twice.
    return [random.choice(data) for i in range(sample_length)]


def find_all_objects(enclosing_directory, extension, files_list):

    # TODO: document
    # Make sure enclosing directory has a finishing /
    if not enclosing_directory.endswith("/"):
        enclosing_directory += "/"

    for f in os.listdir(enclosing_directory):
        # Determine if the item is a directory or not
        entire_path = enclosing_directory + f
        if os.path.isdir(entire_path):

            find_all_objects(entire_path, extension, files_list)
        else:
            if entire_path.endswith(extension):
                files_list.append(entire_path)
    return files_list
    # We technically don't need to return files_list, since changes in it will be reflected in the main program,
    # but often the user will just pass in an empty list without assigning it first. In this case, we need to return
    # something.
