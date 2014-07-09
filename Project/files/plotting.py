# coding=utf-8
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
import matplotlib.colors as mplcol
import matplotlib.cm as cmx
import numpy.polynomial.polynomial as polynomial
import numpy as np
from Project.files import main_functions


def plot_color_mag(image, predictions=True, distinguish_red_sequence=False):
    """
    Makes a color-magnitude plot for the given image. Can plot EzGal predictions and plot RS in red.

    The CMDs are designed to look like the ones in Stanford 2014. The plot dimensions are similar to those.

    :param image: Image object that the data will be taken from.
    :param predictions: Boolean of whether or not to plot the EzGal predictions.
    :param distinguish_red_sequence: Boolean of whether or not to plot the RS members in red.
    :return: first: figure object the CMD was plotted on.
             second: axes object for the CMD itself. This is needed because I need to over plot things later, and
             returning the object is easier than making this function way more complicated than it already is.
    """

    # Need to make lists that can be plotted on the CMD
    # start by initializing empty lists to append to
    non_rs_mags, rs_mags, non_rs_colors, rs_colors, rs_color_errs, non_rs_color_errs = [], [], [], [], [], []
    for gal in image.galaxy_list:
        if distinguish_red_sequence:  # If the user wants the RS in red, we need separate lists for RS and not
            if gal.RS_member:
                rs_mags.append(gal.mag)
                rs_colors.append(gal.color)
                rs_color_errs.append(gal.color_error)
            else:
                non_rs_mags.append(gal.mag)
                non_rs_colors.append(gal.color)
                non_rs_color_errs.append(gal.color_error)
        else:
            non_rs_mags.append(gal.mag)
            non_rs_colors.append(gal.color)
            non_rs_color_errs.append(gal.color_error)

    # Set up the plot
    fig = plt.figure(figsize=(9, 6))
    # Configure subplots
    whole_plot = grid.GridSpec(1, 2, width_ratios=[50, 1], left=0.08, right=0.92, wspace=0.1)
    # Still automatically leave room for the color bar, even if not needed, to make code simpler. It doesn't take up
    #     that much space, so it looks fine blank anyway
    color_mag_ax = plt.subplot(whole_plot[0, 0])

    # the predictions will have a color bar that needs its own axis
    if predictions:
        color_bar_ax = plt.subplot(whole_plot[0, 1])
        # Plot the predictions now
        add_predictions_to_cmd(fig, color_mag_ax, color_bar_ax)

    # Now we can plot the points on the CMD (including errors)
    # check to make sure they have something in them
    if len(non_rs_colors) > 0:
        color_mag_ax.errorbar(x=non_rs_mags, y=non_rs_colors, yerr=non_rs_color_errs, c="k", fmt=".", elinewidth=0.35,
                              capsize=0, markersize=5)
    if len(rs_colors) > 0:
        color_mag_ax.errorbar(x=rs_mags, y=rs_colors, yerr=rs_color_errs, c="r", fmt=".", elinewidth=0.35, capsize=0,
                              markersize=5)  # Only difference is that this is plotted in red.

    color_mag_ax.set_title(image.name + ",  z = " + str(image.spec_z))
    color_mag_ax.set_xlabel(image.filters[1] + " Band Magnitude")
    color_mag_ax.set_ylabel(image.filters[0] + " - " + image.filters[1] + " Color")

    # Change the scale to match Stanford 14. Each filter set will be different
    if image.filters == ["r", "z"]:
        color_mag_ax.set_xlim([20, 23.5])
        # color_mag_ax.set_xlim([18, 26])
        color_mag_ax.set_ylim([0, 3.5])
    elif image.filters == ["i", "[3.6]"]:
        color_mag_ax.set_xlim([18, 21.5])
        color_mag_ax.set_ylim([-.5, 4.5])
    elif image.filters == ["[3.6]", "[4.5]"]:
        color_mag_ax.set_xlim([18.5, 21.5])
        color_mag_ax.set_ylim([-1, 0.5])

    return fig, color_mag_ax


def add_predictions_to_cmd(fig, color_mag_ax, color_bar_ax):
    """
    Plot lines representing the EzGal predictions of the RS for redshifts 0.5 ≤ z ≤ 1.5, with spacing of 0.05.

    Assumes the filter set is r-z
    Todo: Make this work for all available filters

    :param fig: figure object all the axes belong to
    :param color_mag_ax: axes object for plotting the CMD on
    :param color_bar_ax: axes object where the color bar will go
    :return: none. Figure and axes are modified in place
    """

    # first need to get the model's predictions
    predictions_dict = main_functions.make_prediction_dictionary(0.05)
    # Returns a dictionary with keys = redshifts, values = predictions objects

    # Set the colormap, to color code lines by redshift
    spectral = plt.get_cmap("spectral")
    # Normalize the colormap so that the the range of colors maps to the range of redshifts
    c_norm = mplcol.Normalize(vmin=min(predictions_dict), vmax=max(predictions_dict))
    scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=spectral)

    for z in predictions_dict:
        line = predictions_dict[z].rz_line
        xs = line.xs
        ys = line.ys

        # Get color
        color_val = scalar_map.to_rgba(predictions_dict[z].redshift)

        # Plot the predicted line, with the correct color
        color_mag_ax.plot(predictions_dict[z].rz_line.xs, predictions_dict[z].rz_line.ys, color=color_val,
                          linewidth=0.2)

        # Plot the points that correspond to L_star projected at those redshifts
        color_mag_ax.scatter(predictions_dict[z].z_mag,
                             predictions_dict[z].r_mag - predictions_dict[z].z_mag,
                             color=color_val)

    # Add a color bar
    scalar_map.set_array([])  # I don't know what this does, but I do know it needs to be here.
    fig.colorbar(scalar_map, cax=color_bar_ax)
    color_bar_ax.set_ylabel("Redshift")


def plot_residuals(image):
    """
    Plot the color residuals for each galaxy in the image.

    :param image: image object containing all the galaxies
    :return: figure object the plot was made on
    """

    # make lists of the galaxies' color residuals, magnitudes, and errors
    mags, color_residuals, errors = [], [], []
    for gal in image.galaxy_list:
        mags.append(gal.mag)
        color_residuals.append(gal.color_residual)
        errors.append(gal.color_error)

    # Plot them
    fig = plt.figure(figsize=(9, 6))
    # Use gridspec to configure the subplots
    whole_plot = grid.GridSpec(1, 2, width_ratios=[6, 1], left=0.08, right=0.92, wspace=0.0)
    residual_ax = plt.subplot(whole_plot[0])
    histo_ax = plt.subplot(whole_plot[1])

    # Plot the residuals
    residual_ax.errorbar(x=mags, y=color_residuals, yerr=errors, c="k", fmt=".", elinewidth=0.35, capsize=0,
                         markersize=5)
    residual_ax.set_xlim([20, 23.5])
    residual_ax.set_ylim([-1, 1])
    # Plot a line at zero, for easier visual inspection of any residual slope
    residual_ax.axhline(0)
    residual_ax.set_title(str(image.name) + ", spec z = " + str(image.spec_z) + ", photo z = " + str(image.photo_z))
    residual_ax.set_xlabel("z Band Magnitude")
    residual_ax.set_ylabel("Color Difference From Best Fit Model")

    # Plot histogram
    histo_ax.hist(color_residuals, bins=20, range=(-1, 1), orientation="horizontal", color="k")
    # Move the histogram color labels to the right, so they don't overlap the CMD
    histo_ax.yaxis.tick_right()
    # Get rid of the horizontal ticks, since values clutter the plot, and only relative values actually matter here.
    histo_ax.xaxis.set_ticks([])

    return fig


def plot_z_comparison(images, directory, filename):
    """
    Plot and save the spectroscopic redshift vs calculated photometric redshift.

    :param images: list of image objects that contain the two redshifts
    :param directory: Directory where the plot will be saved
    :param filename: Filename the plot will be saved as. Do not include the extension, will always be a .pdf
    :return: none. Plot is saved, though.
    """
    # Make lists of spectroscopic and photometric redshifts, since that's what the plot function takes
    spec, photo, photo_err, weights = [], [], [], []
    for i in images:
        spec.append(float(i.spec_z))
        photo.append(float(i.photo_z))
        photo_err.append(i.photo_z_error)
        weights.append(1.0 / i.photo_z_error)

    # Find the best fit line
    fit = polynomial.polyfit(spec, photo, 1, w=weights)  # returns coefficients of a linear fit
    # Turn these coefficients into a line
    x = np.arange(0, 1.5, 0.01)
    fit_line = fit[0] + x * fit[1]

    # Plot everything
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(1, 1, 1)
    # Plot points for individual images
    ax.errorbar(spec, photo, yerr=photo_err, c="k", fmt=".", capsize=2, elinewidth=0.5)
    # Plot where the best fit line should be
    ax.plot([0.5, 1.5], [0.5, 1.5], "k-", lw=0.5)
    # Plot the best fit line
    ax.plot(x, fit_line, "b")
    # Add a grid, to make for easier viewing
    ax.grid(which="both")
    ax.minorticks_on()
    ax.set_xlabel("Spectroscopic Redshift")
    ax.set_ylabel("Photometric Redshift")
    ax.set_title("Spectroscopic vs Photometric Redshifts")
    ax.set_xlim((0.5, 1.5))
    ax.set_ylim((0.5, 1.5))

    fig.savefig(directory + filename + ".pdf", format="pdf")


def plot_initial_redshift_finding(image, z_list, galaxies_list, best_z):
    # z_list may be in decimal format, so change it to floats
    z_list = [float(z) for z in z_list]

    # Plot the bar plot of galaxies as a function of redshift
    bar_fig = plt.figure(figsize=(6, 5))
    bar_ax = bar_fig.add_subplot(1, 1, 1)
    bar_ax.bar(z_list, galaxies_list, width=0.01, color="0.5", align="center")
    bar_ax.set_title(image.name + ", z = " + str(image.spec_z))
    # Show the cluster's redshift, and the initial redshift the code picked
    bar_ax.axvline(x=image.spec_z, c="r", lw=4)
    bar_ax.axvline(x=best_z, c="k", lw=4)
    plt.savefig("/Users/gbbtz7/GoogleDrive/Research/Plots/InitialZ/" +image.name + "_histo.pdf", format="pdf")