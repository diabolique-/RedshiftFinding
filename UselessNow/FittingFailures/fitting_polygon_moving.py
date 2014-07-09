# contains function used for fitting the redshfit to the cluster
from PhotoZ.files import plotting
import matplotlib.path as path
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import math


def find_rs_redshift_color_cuts(image, fine_predictions,  coarse_predictions, plot_cuts=False):
    """
    Calculate the best fit redshift for the red sequence.

    Starts by finding out which redshift has the most galaxies within 2 sigma of the prediction. That redshift is used
    as the starting point for chi-squared fitting. The chi-squared fitting is done on all galaxies within a color cut of
    the prediction. Since the prediction lines have a slope, the region where galaxies are used to fit is shaped like a
    parallelogram. This is done in the code by making a polygon, then testing whether the galaxies are inside that
    polygon.

    The chi square fit is done on the galaxies within the polygon, then the polygon is made smaller, until the fit
    reaches some level of goodness. The redshift that is the best fit in the final cut is considered the photometric
    redshift of the cluster.

    The plots of the polygon superimposed on the CMD for each cluster can also be plotted.

    :param image: Image object of the image containing the cluster that the photometric redshift will be found for
    :param fine_predictions: dictionary containing keys of redshifts and values containing predictions objects. This
           dictionary should have closer spacing of redshifts, to make fitting more accurate.
    :param coarse_predictions: same as fine_predictions, but containing redshifts spaced farther apart. This wil be used
           to find the initial fit. Coarse resolution is better here because precision isn't needed in the initial
           fit, and having too many redshifts to fit would take a long time.
    :param plot_cuts: boolean of whether or not to plot the CMDs with the polygons overlaid for each cut.
    :return: list of figures, that contains the figures with CMDs and cut polygons.
    """

    # Set placeholders that will be replaced as the chi fitting runs
    best_chi_sq = 999
    cmd_cuts_figs = []  # initialize empty list, will be filled if things are plotted

    # Find the first redshift to start chi-squared fitting
    best_z = find_initial_redshift(image, coarse_predictions)

    iteration = 1.0  # set a counter that will be used in the loop
    # Want to find a fit that is decent
    while best_chi_sq > 1.3:

        # Set placeholders that will be replaced as the chi fitting runs
        best_chi_sq = 999

        # build the polygon that determines the color cuts
        # The polygon will have set magnitude limits, and color limits above and below the best prediction so far. The
        # color cuts will gradually shrink. This will make the code gradually get closer to the correct red sequence.
        # To do this, first we need to get the predicted line of best redshift fit so far
        line = fine_predictions[best_z].rz_line
        # This line will be a list of lists with dimensions [x values, y values] (for the line)
        characteristic_mag = fine_predictions[best_z].z_mag

        # the left and right magnitude cuts will be based on the characteristic magnitude
        left_idx = line[0].index(round(characteristic_mag - 1.2, 2))
        right_idx = line[0].index(round(characteristic_mag + 1.0, 2))

        # Now set the vertices of the cuts polygon using the color of the best fit line
        # As the iterations increase, the color cuts will get smaller (closer to the best fit), which will throw out
        # more and more non-RS galaxies
        top_left = [characteristic_mag - 1.2, line[1][left_idx] + 2.0 / (iteration + 7.0)]
        top_right = [characteristic_mag + 1.0, line[1][right_idx] + 2.0 / (iteration + 7.0)]
        bottom_left = [characteristic_mag - 1.2, line[1][left_idx] - 2.0 / (iteration + 7.0)]
        bottom_right = [characteristic_mag + 1.0, line[1][right_idx] - 2.0 / (iteration + 7.0)]
        # I made this color points complicated to avoid brief changes (ie 1 to 1/2 to 1/3 to 1/4)
        # The numbers were chosen to take the top from 1/2 to 1/5 in 10 iterations, and the bottom from 1/4 to 1/5 in 10

        # Turn these points into a polygon
        codes = [1, 2, 2, 2, 79]  # tell the path what to do [start, move, move, move, close path]
        vertices = [top_left, top_right, bottom_right, bottom_left, top_left]
        polygon = path.Path(vertices, codes)

        # Plot the polygon and best fit line
        if plot_cuts:
            fig, ax = plotting.plot_color_mag(image, predictions=False)
            # Add the cut polygon
            patch = patches.PathPatch(polygon, facecolor='k', alpha=0.3, lw=0)
            ax.add_patch(patch)
            # Add the line of best fit
            ax.plot(line[0], line[1], "k-")
            ax.set_title(image.name + ", spec z = " + str(image.spec_z) + ", current z = " + str(best_z))
            cmd_cuts_figs.append(fig)

        # Now find the new best fit line for the points in the new polygon
        for z in fine_predictions:
            chi_sq = image_chi_square_polygon(image, fine_predictions[z].rz_line, polygon)
            if chi_sq < best_chi_sq:
                best_chi_sq = chi_sq
                best_z = z

        if best_chi_sq == 999:  # This will happen only if the polygon gets too small and includes no galaxies.
            break

        iteration += 1.0

    # Plot the final best fit line
    if plot_cuts:
        line = fine_predictions[best_z].rz_line
        fig, ax = plotting.plot_color_mag(image, predictions=False)
        # Add the line of best fit
        ax.plot(line[0], line[1], "k-", linewidth=1.5)
        ax.set_title(image.name + ", spec z = " + str(image.spec_z) + ", photo z = " + str(best_z))
        cmd_cuts_figs.append(fig)

    # Set the images photometric redshift instance attribute
    image.photo_z = best_z

    # Set the color residuals for all the galaxies using the best fit model line
    set_residuals(image, fine_predictions[best_z].rz_line)

    return cmd_cuts_figs



def image_chi_square_polygon(image, model_line, polygon):
    """
    Calculate the reduced chi-squared value for the fit of the given line on the galaxies within the polygon.

    Reduced chi-squared = sum(((model - data)/error)**2) / number of data points

    :param image: Image object of the cluster to be fitted
    :param model_line: Line that will be fitted to the data. List of lists with dimensions[[x values], [y values]]
    :param polygon: Polygon of cuts. Only galaxies inside the polygon (within the cuts) will be kept.
    :return: Reduced chi-squared value
    """
    # Initialize placeholders
    chi_sq = 0
    good_galaxies = 0
    for gal in image.galaxy_list:
        # Some galaxies are clear outliers, or have bad data
        # only use points that are inside the polygon I want
        if 0.001 < gal.color_error < 10 and polygon.contains_point([gal.mag, gal.color]):
            good_galaxies += 1
            # find color model predictions for the galaxy at the given magnitude
            idx = model_line[0].index(gal.mag)
            chi_sq += ((model_line[1][idx] - gal.color) / gal.color_error)**2
    if good_galaxies > 1:
        return chi_sq / good_galaxies
    else:
        return 999


def find_initial_redshift(image, predictions, plot_bar=False):
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
    for z in sorted(predictions.iterkeys()):  # need to be sorted, since we will be finding local maxima later
        galaxies = 0
        # For each galaxy, find out whether it is a RS member if the cluster is at that redshift
        for gal in image.galaxy_list:
            if predictions[z].z_mag - 1.2 < gal.mag < predictions[z].z_mag + 0.8 and gal.color_error < 0.5:
                idx = predictions[z].rz_line[0].index(gal.mag)
                # If it's within 1.5 sigma, increment galaxy counter
                if abs((predictions[z].rz_line[1][idx] - gal.color) / gal.color_error) < 1.5:
                    galaxies += 1

        # Append the results to lists
        galaxies_list.append(galaxies)
        z_list.append(z)

    # The best redshift will be the most, but sometimes the most appears at a very low redshift that is wrong. A better
    # way is to find all the significant local maxima, then pick the one of those at the highest redshift
    highest_sum = 0
    best_z = 0
    for k in range(2, len(z_list)-2):
        temp_sum = galaxies_list[k-2] + galaxies_list[k-1] + galaxies_list[k] + galaxies_list[k+1] + galaxies_list[k+2]
        if temp_sum > highest_sum:
            highest_sum = temp_sum
            best_z = z_list[k]

    if plot_bar:
        # Plot the bar plot of galaxies as a function of redshift
        bar_fig = plt.figure(figsize=(6, 5))
        bar_ax = bar_fig.add_subplot(1, 1, 1)
        bar_ax.bar(z_list, galaxies_list, width=0.02, color="0.5", align="center")
        bar_ax.set_title(image.name + ", z = " + str(image.spec_z))
        # Show the cluster's redshift, and the initial redshift the code picked
        bar_ax.axvline(x=image.spec_z, c="r", lw=4)
        bar_ax.axvline(x=best_z, c="k", lw=4)
        plt.savefig("/Users/gbbtz7/GoogleDrive/Research/Plots/InitialZ/" +image.name + "_histo.pdf", format="pdf")

    return best_z





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
            idx = best_z_line[0].index(gal.mag)
            gal.color_residual = gal.color - best_z_line[1][idx]
        else:
            gal.color_residual = 999


