from Project.files import classes
from matplotlib.backends.backend_pdf import PdfPages
import ezgal
import numpy as np
import cPickle


def read_image_objects(file_path="/Users/gbbtz7/GoogleDrive/Research/Data/images.pickle"):
    """
    Returns the object stored by the pickle module.
    :param file_path: place where the pickled file is stored.
    :return: whatever is stored in the pickled object
    """
    return cPickle.load(open(file_path, "r"))


def make_prediction_dictionary(spacing):
    """
    Use the EzGal module to get model predictions, find correct slopes of RS, and turn this info into a dictionary where
    keys are redshifts, and values are objects storing all the data about the model prediction for that redshift

    :param spacing: float of how far apart the redshift predictions will be.
    :return: dictionary, where keys=redshifts and values=predictions object
    """

    # Make the models
    # For simplicity right now, just use the 0.1 gyr exponential model
    # Todo: Make this work to fit the actual data. This simple model will not work.
    model = ezgal.ezgal("bc03_exp_0.1_z_0.02_chab_evolved_zf_3.0_ugrizch1ch2.model")

    # Set formation redshift and observed redshifts
    zf = 3.0
    zs = np.arange(0.5, 1.5000001, spacing)


    # Normalize to Dai et al 2009
    # model.set_normalization(filter='ch1', mag=-25.06, apparent=False, vega=True, z=0.24)
    # Normalize to Coma
    model.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

    # Calculate observables
    mags = model.get_apparent_mags(zf, filters=["sloan_r", "sloan_i", "sloan_z", "ch1", "ch2"], zs=zs, vega=False)
    # If the filters are changed, then the way the magnitudes are passed into the prediction object needs to be changed
    #     as well. That work depends on the index of the specific filters
    # dimensions of mags: [redshifts, filters]

    # Now need to get slopes for all redshifts
    # The info here is stored in a file, so reading that will be all we need
    load_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/Best_fit_RS_slope.pickle")
    slope_dict = cPickle.load(load_file)
    # slope_dict is a dictionary of keys = redshifts, values = slopes
    load_file.close()

    # Initialize an empty list
    predictions_dict = dict()

    for i in range(len(zs)):
        predictions_dict[zs[i]] = classes.Predictions(redshift=zs[i],
                                                                r_mag=mags[i][0],  # need to specify which filter
                                                                i_mag=mags[i][1],
                                                                z_mag=mags[i][2],
                                                                ch1_mag=mags[i][3],
                                                                ch2_mag=mags[i][4],
                                                                slope=slope_dict[round(zs[i], 2)])
        # zs are rounded, since they get floating point errors somewhere. They are like 0.60000004 before rounding.

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
    for obj in figs:
        pp.savefig(obj)
    pp.close()