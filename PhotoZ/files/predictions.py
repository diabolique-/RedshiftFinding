import ezgal
import numpy as np
import cPickle
from PhotoZ.files import other_classes

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



    # Set formation redshift and observed redshifts
    zf = 3.0
    zs = np.arange(0.5, 1.5000001, spacing)

    # Normalize to Coma
    model.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

    # Calculate observables in AB mags
    mags = model.get_apparent_mags(zf, filters=["sloan_r", "sloan_i", "sloan_z", "ch1", "ch2"], zs=zs, vega=False)
    # If the filters are changed, then the way the magnitudes are passed into the prediction object needs to be
    # changed as well. That work depends on the index of the specific filters
    # dimensions of mags: [redshifts, filters]

    # Now need to get slopes for all redshifts
    # The info here is stored in a file, so reading that will be all we need
    load_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/CodeData/Best_fit_RS_slope.pickle")
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


def simple_chi_square(sources, color, band, model_line):
    """Does a simple reduced chi-square fit for a list of sources to a model line.

    Doesn't do any filtering. All sources passed in will be used. If any filtering of the sources is needed, do that
    outside this function.

    :param sources: List of sources to be included in the fit
    :param model_line: Line object holding data that represents the model's predictions we are fitting to
    :return: reduced chi-squared value
    """
    # Initialize some placeholders
    chi_sq = 0
    for source in sources:
        # find color model predictions for the galaxy at the given magnitude
        idx = model_line.xs.index(round(source.mags[band].value, 2))
        chi_sq += ((model_line.ys[idx] - source.colors[color].value) / source.colors[color].error)**2
    # Reduced chi squared takes the total chi squared value and divides by degrees of freedom.
    # Degrees of freedom = number of data points - number of parameters (redshift, in this case) - 1
    return chi_sq / (len(sources) - 1 - 1)