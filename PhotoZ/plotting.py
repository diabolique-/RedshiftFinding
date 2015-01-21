# coding=utf-8
from PhotoZ import predictions
from PhotoZ import global_paths
import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
import matplotlib.colors as mplcol
import matplotlib.cm as cmx
import numpy as np

# TODO: document


def plot_color_mag(cluster, color, band, predictions=True, distinguish_red_sequence=False, return_axis=False):
    """
    Makes a color-magnitude plot for the given cluster. Can plot EzGal predictions and plot RS in red.

    The CMDs are designed to look like the ones in Stanford 2014. The plot dimensions are similar to those.

    :param cluster: Cluster object that the data will be taken from.
    :param color: string holding color to be plotted on te y axis. Should be of the form "band1-band2"
    :param band: string telling which band's magnitudes will be plotted on the x axis.
    :param predictions: Boolean of whether or not to plot the EzGal predictions.
    :param distinguish_red_sequence: Boolean of whether or not to plot the RS members in red.
    :return: first: figure object the CMD was plotted on.
             second: axes object for the CMD itself. This is needed because I need to over plot things later, and
             returning the object is easier than making this function way more complicated than it already is.
    """
    # Need to make lists that can be plotted on the CMD
    valid_sources = [source for source in cluster.sources_list if (color in source.colors and band in source.mags and
                                                                   source.colors[color].error < 5.0 and
                                                                   source.in_location)]
    # start by initializing empty lists to append to
    non_rs_mags, rs_mags, non_rs_colors, rs_colors, rs_color_errs, non_rs_color_errs = [], [], [], [], [], []
    if distinguish_red_sequence:
        # The many if statements are to make sure only objects with the right data are included
        rs_mags = [source.mags[band].value for source in valid_sources if source.RS_member]
        non_rs_mags = [source.mags[band].value for source in valid_sources if not source.RS_member]
        rs_colors = [source.colors[color].value for source in valid_sources if source.RS_member]
        non_rs_colors = [source.colors[color].value for source in valid_sources if not source.RS_member]
        rs_color_errs = [source.colors[color].error for source in valid_sources if source.RS_member]
        non_rs_color_errs = [source.colors[color].error for source in valid_sources if not source.RS_member]
    else:  # use non_rs lists
        non_rs_mags = [source.mags[band].value for source in valid_sources]
        non_rs_colors = [source.colors[color].value for source in valid_sources]
        non_rs_color_errs = [source.colors[color].error for source in valid_sources]



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
        _add_predictions_to_cmd(fig, color_mag_ax, color_bar_ax, color)

    # Now we can plot the points on the CMD (including errors)
    # check to make sure they have something in them
    if len(non_rs_colors) > 0:
        color_mag_ax.errorbar(x=non_rs_mags, y=non_rs_colors, yerr=non_rs_color_errs, c="k", fmt=".", elinewidth=0.35,
                              capsize=0, markersize=5)
    if len(rs_colors) > 0:
        color_mag_ax.errorbar(x=rs_mags, y=rs_colors, yerr=rs_color_errs, c="r", fmt=".", elinewidth=0.35, capsize=0,
                              markersize=5)  # Only difference is that this is plotted in red.

    color_mag_ax.set_title(cluster.name)
    color_mag_ax.set_xlabel(band)
    color_mag_ax.set_ylabel(color)

    # Change the scale to match Stanford 14. Each filter set will be different
    if color == "sloan_r-sloan_z":
        color_mag_ax.set_xlim([20, 23.5])  # should be [20, 23.5] Changed to see high redshift better
        # color_mag_ax.set_xlim([20, 26])
        color_mag_ax.set_ylim([0, 3.5])
    elif color == "sloan_i-ch1":
        color_mag_ax.set_xlim([18, 21.5])
        color_mag_ax.set_ylim([-.5, 4.5])
    elif color == "ch1-ch2":
        color_mag_ax.set_xlim([18.5, 21.5])
        color_mag_ax.set_ylim([-1, 0.5])


    if return_axis:
        return fig, color_mag_ax
    else:
        return fig


def _add_predictions_to_cmd(fig, color_mag_ax, color_bar_ax, color):
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
    predictions_dict = predictions.make_prediction_dictionary(0.05)
    # Returns a dictionary with keys = redshifts, values = predictions objects

    # Set the colormap, to color code lines by redshift
    spectral = plt.get_cmap("spectral")
    # Normalize the colormap so that the the range of colors maps to the range of redshifts
    c_norm = mplcol.Normalize(vmin=min(predictions_dict), vmax=max(predictions_dict))
    scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=spectral)

    for z in predictions_dict:
        color_val = scalar_map.to_rgba(predictions_dict[z].redshift)


        function = predictions_dict[z].get_lambda(color)
        xs = np.arange(17, 25, 0.01)
        ys = [function(x) for x in xs]

        # Plot the predicted line, with the correct color
        color_mag_ax.plot(xs, ys, color=color_val, linewidth=0.2)

        # turn color into two bands
        bluer_band, redder_band = color.split("-")

        # Plot the points that correspond to L_star projected at those redshifts
        color_mag_ax.scatter(predictions_dict[z].mags_dict[redder_band],
                             predictions_dict[z].mags_dict[bluer_band] - predictions_dict[z].mags_dict[redder_band],
                             color=color_val)

    # Add a color bar. It works on GEG computer, but not home computer, for some reason.
    scalar_map.set_array([])  # I don't know what this does, but I do know it needs to be here.
    fig.colorbar(scalar_map, cax=color_bar_ax)
    color_bar_ax.set_ylabel("Redshift")


def plot_residuals(cluster):
    """
    Plot the color residuals for each galaxy in the image.

    :param cluster: cluster object containing all the galaxies
    :return: figure object the plot was made on
    """

    # make lists of the galaxies' color residuals, magnitudes, and errors
    mags, color_residuals, errors = [], [], []
    for gal in cluster.galaxy_list:
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
    residual_ax.set_title(str(cluster.name) + ", spec z = " + str(cluster.spec_z) +
                          ", photo z = " + str(cluster.photo_z))
    residual_ax.set_xlabel("z Band Magnitude")
    residual_ax.set_ylabel("Color Difference From Best Fit Model")

    # Plot histogram
    histo_ax.hist(color_residuals, bins=20, range=(-1, 1), orientation="horizontal", color="k")
    # Move the histogram color labels to the right, so they don't overlap the CMD
    histo_ax.yaxis.tick_right()
    # Get rid of the horizontal ticks, since values clutter the plot, and only relative values actually matter here.
    histo_ax.xaxis.set_ticks([])

    return fig


def plot_z_comparison(clusters, color, fit=None, label=None):
    """
    Plot and save the spectroscopic redshift vs calculated photometric redshift.

    :param clusters: list of image objects that contain the two redshifts
    :param directory: Directory where the plot will be saved
    :param filename: Filename the plot will be saved as. Do not include the extension, will always be a .pdf
    :return: none. Plot is saved, though.
    """
    # Make lists of spectroscopic and photometric redshifts, since that's what the plot function takes
    spec, photo, upper_photo_err, lower_photo_err, weights = [], [], [], [], []
    for c in clusters:
        if c.spec_z and color in c.rs_z:  # Can't plot comparison if the cluster doesn't have a spectroscopic redshift
            spec.append(float(c.spec_z))
            photo.append(float(c.rs_z[color]))
            lower_photo_err.append(c.lower_photo_z_error[color])
            upper_photo_err.append(c.upper_photo_z_error[color])
            # weights.append(1.0 / ((c.upper_photo_z_error + c.lower_photo_z_error)/2))  # Average the errors
            # TODO: Find a better way to do the weighting for the fit. Simple averaging of the errors is WRONG.
    total_error = [lower_photo_err, upper_photo_err]  # goes into the lopsided error bars

    # # Find the best fit line
    # fit = polynomial.polyfit(spec, photo, 1, w=weights)  # returns coefficients of a linear fit
    # # Turn these coefficients into a line
    x = np.arange(0, 1.5, 0.01)



    # Plot everything
    # TODO: make work with lopsided error bars
    fig = plt.figure(figsize=(5, 5))
    ax = fig.add_subplot(1, 1, 1)
    # Plot points for individual clusters
    ax.errorbar(photo, spec, xerr=total_error, c="k", fmt=".", capsize=2, elinewidth=0.5, markersize=8)
    # Plot where the best fit line should be
    ax.plot([0.5, 2.5], [0.5, 2.5], "k-", lw=0.5)
    # Plot the best fit line
    if fit is not None:  # If we want to plot the fit
        # turn the fit into something that can be plotted
        fit_line = 0
        for coefficient in range(len(fit)):
            fit_line += fit[coefficient]*x**(coefficient)
            # acually plot it
        ax.plot(x, fit_line, "b")
    # label the data points with the cluster name
    if label:
        for c in clusters:
            if c.spec_z and color in c.rs_z:
                xy = (c.rs_z[color], c.spec_z)
                ax.annotate(s=c.name, xy=xy, xytext=(0,-7), textcoords="offset points", size=4, rotation='vertical')
    # Add a grid, to make for easier viewing
    ax.grid(which="both")
    ax.minorticks_on()
    ax.set_ylabel("Spectroscopic Redshift")
    ax.set_xlabel("Red Sequence Redshift")
    ax.set_title(color)
    ax.set_xlim((0.8, 1.3))
    ax.set_ylim((0.8, 1.3))

    return fig


def plot_initial_redshift_finding(cluster, z_list, galaxies_list, best_z):
    """Plots a bar graph of the number of galaxies at the RS for each redshift.

    :param cluster: Cluster object in the plot
    :param z_list: list of redshifts that were used in the calculation
    :param galaxies_list: list of galaxies near each redshift. Needs to be the same length as z_list, and the numbers
           in galaxies_list should correspond with the redshifts in z_list
    :param best_z: Redshift calculated as the best fit
    :return: None, but plot is saved.
    """
    # z_list may be in string format, so change it to floats
    z_list = [float(z) for z in z_list]

    # Plot the bar plot of galaxies as a function of redshift
    bar_fig = plt.figure(figsize=(6, 5))
    bar_ax = bar_fig.add_subplot(1, 1, 1)
    bar_ax.bar(z_list, galaxies_list, width=0.01, color="0.5", align="center")
    bar_ax.set_title(cluster.name + ", z = " + str(cluster.spec_z))
    # Show the cluster's redshift, and the initial redshift the code picked
    bar_ax.axvline(x=cluster.spec_z, c="r", lw=4)
    bar_ax.axvline(x=best_z, c="k", lw=4)
    return bar_fig


def plot_fitting_procedure(cluster, color, band, redshift, other_info=None, color_red_sequence=True):
    """Plot the red sequence members for the cluster on a CMD, with a line indicating the redshift of the current fit.

    :param cluster: Cluster that holds info that will be plotted
    :param redshift: Redshift for the prediction line that will be plotted
    :param other_info: Info that will go into the subtitle.
    :return: figure holding the plot
    """
    bluer_band, redder_band = color.split("-")
    fig, ax = plot_color_mag(cluster, color=color, band=redder_band, predictions=False,
                                                                      distinguish_red_sequence=color_red_sequence,
                             return_axis=True)
    line = cluster.predictions_dict[redshift].get_lambda(color)
    mags = np.arange(10, 30, 0.01)
    colors = [line(mag) for mag in mags]
    ax.plot(mags, colors, "k-", linewidth=0.5, label="Initial z")
    ax.scatter(cluster.predictions_dict[redshift].mags_dict[redder_band], cluster.predictions_dict[redshift].mags_dict[
               bluer_band] - cluster.predictions_dict[redshift].mags_dict[redder_band], c="r", s=10)
                # Plot characteristic magnitude point
    fig.suptitle(cluster.name + ", current z=" + str(redshift))
    ax.set_title(str(other_info), fontsize=10)

    return fig


def plot_location(cluster):

    # make lists of ra and dec for 3 cases: red sequence members, non-rs members inside location cut, non rs-member
    # outisde location cut
    rs_decs, rs_ras, loc_non_rs_ras, loc_non_rs_decs, non_loc_non_rs_ras, non_loc_non_rs_decs = [], [], [], [], [], []
    for source in cluster.sources_list:
        if source.RS_member:
            rs_ras.append(source.ra)
            rs_decs.append(source.dec)
        else:
            if source.in_location:
                loc_non_rs_ras.append(source.ra)
                loc_non_rs_decs.append(source.dec)
            else:
                non_loc_non_rs_ras.append(source.ra)
                non_loc_non_rs_decs.append(source.dec)

    # Then plot them
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)
    # Have to check length of arrays, since 0 length lists can't be plotted
    if non_loc_non_rs_decs and non_loc_non_rs_ras:
        ax.scatter(non_loc_non_rs_ras, non_loc_non_rs_decs, c="0.2", s=2, linewidth=0)
    if loc_non_rs_decs and loc_non_rs_ras:
        ax.scatter(loc_non_rs_ras, loc_non_rs_decs, c="k", s=3)
    if rs_decs and rs_ras:
        ax.scatter(rs_ras, rs_decs, c="r", s=6, edgecolors=None, linewidth=0)  # don't want black borders
    ax.set_title(cluster.name)
    ax.set_xlabel("RA")
    ax.set_ylabel("Dec")
    # make ra go from right to left
    plt.gca().invert_xaxis()

    return fig

def plot_chi_data(cluster, chi_redshift_pairs, left_limit, best_z, right_limit):
    # TODO: document
    redshifts, chi_squared_values = [], []
    for pair in chi_redshift_pairs:
        redshifts.append(pair[0])
        chi_squared_values.append(pair[1])
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1)
    ax.plot(redshifts, chi_squared_values, "k-")
    ax.scatter([float(left_limit), float(best_z), float(right_limit)], [1.0, 1.0, 1.0])
    ax.set_ylim((0.0, 5.0))
    ax.set_xlabel("Redshift")
    ax.set_ylabel("Chi squared value")
    ax.set_title(cluster.name + ", spec z = " + str(cluster.spec_z))

    return fig
