# contains function used for fitting the redshfit to the cluster
from Project.files import plotting
import math
import random
import numpy as np
import decimal


def fit_z(image, predictions):

    # Set placeholders that will be replaced as the chi fitting runs
    cmd_cuts_figs = []  # initialize empty list, will be filled if things are plotted

    # Find the first redshift to start chi-squared fitting
    best_z = find_initial_redshift(image, predictions)
    set_as_initial_rs_member(image, best_z, predictions)
    fig, ax = plotting.plot_color_mag(image, predictions=False, distinguish_red_sequence=True)

    line = predictions[best_z].rz_line
    ax.plot(line.xs, line.ys, "k:", linewidth=0.5, label="Initial z")

    # Use the bootstrap
    bootstrap(image, predictions)

    # Add the line of best fit
    best_fit_line = predictions[image.photo_z].rz_line
    ax.plot(best_fit_line.xs, best_fit_line.ys, "k-", linewidth=0.5, label="Photo z")
    ax.legend(loc=0)
    ax.set_title(image.name + ", spec z = " + str(image.spec_z) + ", photo z = " + str(image.photo_z) +
                 ", initial z = " + str(best_z))
    cmd_cuts_figs.append(fig)

    return fig


def find_initial_redshift(image, predictions, plot_bar=True):
    """
    Find the intial redshift that is a rough guess of the cluster's redshift, using galaxy counts around the prediction.

    For all the redshifts, count the number of galaxies within 2 simga of the predicted RS line. The redshift that has
    the most galaxies near the RS is the best estimate.

    Some images may seem to contain two red sequences, so pick the higher redshift one, since that is more likely to be
    the actual red sequence of a cluster at high redshift.

    :param image: image object that has the data for the cluster
    :param predictions: dictionary holding predictions for all redshifts. Like one returned by
           Projects/files/models.make_prediction_dictionary().
    :return: float; best estimate of the redshift of the cluster
    """
    # Initialize empty lists, will append as we go
    galaxies_list = []
    z_list = []

    # Iterate through each redshift we have predictions for
    for z in sorted(predictions.iterkeys()):  # need to be sorted, since we will be finding highest point later
        galaxies = 0
        # For each galaxy, find out whether it is a RS member if the cluster is at that redshift
        for gal in image.galaxy_list:
            if predictions[z].z_mag - 1.2 < gal.mag < predictions[z].z_mag + 0.8 and gal.color_error < 0.5:
                idx = predictions[z].rz_line.xs.index(gal.mag)
                # If it's within 1.5 sigma, increment galaxy counter
                if abs((predictions[z].rz_line.ys[idx] - gal.color) / gal.color_error) < 1.5:
                    galaxies += 1

        # Append the results to lists
        galaxies_list.append(galaxies)
        z_list.append(z)

    # The best redshift will be the one with the most RS galaxies. Since the data is noisy, adding the 2 neighbors on
    # each side will make for more stable results
    highest_sum = 0
    best_z = 0
    for k in range(2, len(z_list)-2):
        temp_sum = galaxies_list[k-2] + galaxies_list[k-1] + galaxies_list[k] + galaxies_list[k+1] + galaxies_list[k+2]
        if temp_sum > highest_sum:
            highest_sum = temp_sum
            best_z = z_list[k]

    if plot_bar:
        plotting.plot_initial_redshift_finding(image, z_list, galaxies_list, best_z)

    return best_z


def set_as_initial_rs_member(image, initial_z, predictions):
    """Find which galaxies in the image should be considered as part of the red sequence.

    :param image: image object
    :param initial_z: Redshift identified as the potential photometric redshift.
    :param predictions: predictions object
    :return: none. Galaxy objects have an instance variable changed to indentify them as part of the RS
    """
    for gal in image.galaxy_list:
        # If they are in a magnitude cut around L*
        if predictions[initial_z].z_mag - 2.0 < gal.mag < predictions[initial_z].z_mag + 0.8:
            # Find the place we can find the predicted color.
            idx = predictions[initial_z].rz_line.xs.index(gal.mag)
            # If it's within 2 sigma, it's a member
            if calculate_sigma(gal, predictions[initial_z].rz_line.ys[idx]) < 5.0:
                gal.RS_member = True
    # TODO: Plot locations of the members. See if there is clustering in the very center.


def set_residuals(image, best_z_line):
    """
    Set each galaxy's color_residual instance attribute to the difference between the predicted RS color and the
    galaxy's color

    :param image:image object with data for all galaxies
    :param best_z_line: list of lists that represent the predicted RS line at the cluster's photometric redshift.
           will have dimensions of [x values, y values]
    :return: none. Sets the instance attributes for all galaxy objects, though
    """
    for gal in image.galaxy_list:
        if 18 < gal.mag < 30:  # The line used doesn't extend beyond these points, so there will be nothing to compare
            idx = best_z_line.xs.index(gal.mag)
            gal.color_residual = gal.color - best_z_line.ys[idx]
        else:
            gal.color_residual = 999


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
    :param model_line:
    :return: reduced chi-squared value
    """
    # TODO: fix model_line documentation once line object is made
    # Initialize some placeholders
    chi_sq = 0
    for gal in galaxies:
        # find color model predictions for the galaxy at the given magnitude
        idx = model_line.xs.index(gal.mag)
        chi_sq += ((model_line.ys[idx] - gal.color) / gal.color_error)**2
    # Reduced chi squared takes the total chi squared value and divides by degrees of freedom.
    # Degrees of freedom = number of data points - number of parameters (redshift, in this case) - 1
    return chi_sq / (len(galaxies) - 1 - 1)


def bootstrap(image, predictions):
    """

    :param image:
    :param predictions:
    :return:
    """
    rs_members = [gal for gal in image.galaxy_list if gal.RS_member]
    z_list = []

    for i in range(0, 100):
        sample = sample_with_replacement(rs_members, len(rs_members))
        best_chi_sq = 999
        best_z = 999
        for z in predictions:
            temp_chi_squared = simple_chi_square(sample, predictions[z].rz_line)
            if temp_chi_squared < best_chi_sq:
                best_z = z
                best_chi_sq = temp_chi_squared
        z_list.append(best_z)

    # the numpy median and standard deviation functions don't play nice with decimal numbers, so we need to make floats
    float_z_list = [float(z) for z in z_list]
    # The photometric redshift should still be in decimal format, so do some fancy wrangling to get it there
    image.photo_z = decimal.Decimal(str(round(np.median(float_z_list), 2)))
    image.photo_z_error = np.std(float_z_list)  # Is fine as a float


def sample_with_replacement(data, sample_length):
    """Creates a reandom sample with replacement, for use with bootstrapping.

    :param data: List of data points
    :param sample_length: length of desired sample
    :return: new sample, with random sampling with replacement
    """
    # Pick the desired number of random data points. Data points can be selected twice.
    return [random.choice(data) for i in range(sample_length)]