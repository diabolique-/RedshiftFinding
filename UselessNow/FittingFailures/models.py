import ezgal
import numpy as np
import cPickle


def make_model_lines(z, filters, predictions):
    """
    Makes list of x and y that correspond to a line on the CMD as predicted by the plot
    :param z: redshift of the line
    :param filters: filters used on the CMD
    :param predictions: dictionary of predictions, one returned by get_model_predictions() will work nicely
    :return: lists of x and y that make a line, and the magnitude and color of a galaxy of characteristic luminosity
    according to the luminosity function.
    """

    # Need filter info to tell what filters to use here
    # The numbers we assign correspond to the indices in the list of magnitudes that point to the magnitudes for the
    #   correct filters
    if filters == ["r", "z"]:
        filter_idx = [0, 2]
    elif filters == ["i", "[3.6]"]:
        filter_idx = [1, 3]
    elif filters == ["[3.6]", "[4.5]"]:
        filter_idx = [3, 4]
    else:
        filter_idx = 0

    slope = get_slope(z)

    # get the point for L_star the models predict
    l_star_mag = predictions[z][filter_idx[1]]
    l_star_color = predictions[z][filter_idx[0]]-predictions[z][filter_idx[1]]

    # Now make more points that form a line of the correct slope
    xs = np.arange(l_star_mag - 10, l_star_mag + 10, 0.01).tolist()
    # Use a rearranged point slope form to find the equation for color
    # y-y1 = m(x-x1)
    # y = mx - mx1 + y1
    # Where m=slope, x1=l_star mag, y1=l_star color
    ys = [slope*x - slope*l_star_mag + l_star_color for x in xs]

    return xs, ys, l_star_mag, l_star_color


def get_model_predictions(spacing=0.05):
    """
    Get the predictions that the EzGal model makes for mags as a function of redshift

    :return: dictionary of keys=redshift, values=magnitudes in r, i, z, [3.6], [4.5] at that redshift
    """

    # Make the models
    # For simplicity right now, just use the 0.1 gyr exponential model
    # THIS WILL HAVE TO CHANGE IN THE FUTURE!!!!!!
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
    # dimensions of mags: [redshifts, filters]

    # turn this data into a dictionary, with the keys as redshifts, and values are the list of mags at that z
    # This will make it easier to get the mags for later reference in other functions
    z_color_dict = {zs[i]: mags[i] for i in range(len(zs))}

    return z_color_dict


def get_slope(z):

    # read in the pickled file with the line in it
    load_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/Best_fit_RS_slope.pickle")
    slope_line = cPickle.load(load_file)
    load_file.close()

    # Round z, to make sure it is in the dictionary
    z = round(z, 2)  # 2 digits after the decimal place

    # slope_line is a dictionary of keys = redshifts, values = slopes
    return slope_line[z]