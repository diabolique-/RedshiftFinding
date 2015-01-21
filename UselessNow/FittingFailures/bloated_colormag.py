import matplotlib.pyplot as plt
import matplotlib.gridspec as grid
import matplotlib.colors as mplcol
import matplotlib.cm as cmx

from PhotoZ.files import models


def make_color_mag_plot(image, histogram=False, predictions=True, residuals=False):
    """Plot a color magnitude diagram, and return the figure it was plotted on. Can plot a color histogram as well,
    and will include predictions of color from EzGal.
    """

    # Need to make lists that can be plotted on the CMD
    # start by initializing empty lists to append to
    non_rs_mags, rs_mags, non_rs_colors, rs_colors, rs_color_errs, non_rs_color_errs = [], [], [], [], [], []
    for gal in image.galaxy_list:
        if gal.RS_member == True:
            rs_mags.append(gal.mag)
            if not residuals: # plot color
                rs_colors.append(gal.color)
            else: # plot residuals
                rs_color_errs.append(gal.color_residual)
            rs_color_errs.append(gal.color_error)
        else:
            non_rs_mags.append(gal.mag)
            if not residuals:  #plot color
                non_rs_colors.append(gal.color)
            else:
                non_rs_colors.append(gal.color_residual)
            non_rs_color_errs.append(gal.color_error)




    # Set up axes
    fig = plt.figure(figsize=(9, 6))

    # if there is a histogram, spacing needs to be different
    if histogram:
        # Spacing will be different, so will use multiple axes creations
        whole_plot = grid.GridSpec(1, 2, width_ratios=[50, 1], left=0.08, right=0.92, wspace=0.2)
        # Still automatically leave room for the color bar, even if not needed, to make code simpler. It doesn't take up
        #     that much space, so it looks fine blank anyway
        left_half = grid.GridSpecFromSubplotSpec(1, 2, subplot_spec=whole_plot[0], width_ratios=[5, 1], wspace=0.01)

        # assign axes to these subplots
        color_mag_ax = plt.subplot(left_half[0, 0])
        histogram_ax = plt.subplot(left_half[0, 1])

        # Call the function to plot the histogram
        add_histogram(non_rs_colors, image.filters, histogram_ax)

    else:  # No histogram
        # Configure subplots
        whole_plot = grid.GridSpec(1, 2, width_ratios=[50, 1], left=0.08, right=0.92, wspace=0.1)
        # Still automatically leave room for the color bar, even if not needed, to make code simpler. It doesn't take up
        #     that much space, so it looks fine blank anyway
        color_mag_ax = plt.subplot(whole_plot[0, 0])

    # the predictions will have a color bar that needs its own axis
    if predictions:
        color_bar_ax = plt.subplot(whole_plot[0, 1])
        # Plot the predictions now
        plot_predictions(fig, color_mag_ax, color_bar_ax, image.filters)

    # Now we can plot the points on the CMD (including errors)
    # check to make sure they have something in them
    if len(non_rs_colors) > 0:
        color_mag_ax.errorbar(x=non_rs_mags, y=non_rs_colors, yerr=non_rs_color_errs, c="k", fmt=".", elinewidth=0.35,
                              capsize=0,markersize=5)
    if len(rs_colors) > 0:
        color_mag_ax.errorbar(x=rs_mags, y=rs_colors, yerr=rs_color_errs, c="r", fmt=".", elinewidth=0.35, capsize=0,
                              markersize=5)

    # Set the title
    color_mag_ax.set_title(image.name + ",  z = " + str(image.spec_z))

    # Make x and y labels based on the filters this plot uses
    color_mag_ax.set_xlabel(image.filters[1] + " Band Magnitude")
    color_mag_ax.set_ylabel(image.filters[0] + " - " + image.filters[1] + " Color")

    # Change the scale to match Stanford 14. Each filter set will be different
    if image.filters == ["r", "z"]:
        color_mag_ax.set_xlim([20, 23.5])
        color_mag_ax.set_ylim([0, 3.5])
    elif image.filters == ["i", "[3.6]"]:
        color_mag_ax.set_xlim([18, 21.5])
        color_mag_ax.set_ylim([-.5, 4.5])
    elif image.filters == ["[3.6]", "[4.5]"]:
        color_mag_ax.set_xlim([18.5, 21.5])
        color_mag_ax.set_ylim([-1, 0.5])

    return fig, color_mag_ax


def add_histogram(colors, filters, histogram_ax):
    """
    Adds a color histogram to the color-magnitude diagram.

    :param colors: list of fitted_colors that will be turned into a histogram
    :param filters: list of filters that the fitted_colors are in. Will be used to set limits and labels
    :return: none. The histogram_ax is modified in place
    """

    # Plot the histogram
    # The placement of the histogram depends on the filters used
    if filters == ["r", "z"]:
        histogram_ax.hist(colors, bins=20, range=(0, 3.5), orientation="horizontal", color="k")
        histogram_ax.set_ylim([0, 3.5])
    elif filters == ["i", "[3.6]"]:
        histogram_ax.hist(colors, bins=20, range=(-0.5, 4.5), orientation="horizontal", color="k")
        histogram_ax.set_ylim([-0.5, 4.5])
    elif filters == ["[3.6]", "[4.5]"]:
        histogram_ax.hist(colors, bins=20, range=(-1, 0.5), orientation="horizontal", color="k")
        histogram_ax.set_ylim([-1, 0.5])

    # Move the histogram color labels to the right, so they don't overlap the CMD
    histogram_ax.yaxis.tick_right()

    # Get rid of the horizontal ticks
    histogram_ax.xaxis.set_ticks([])


def plot_predictions(fig, color_mag_ax, color_bar_ax, filters):
    """
    Plot the model predictions_dict onto the CMD.

    :param fig: figure object all the axes belong to
    :param color_mag_ax: axes object for plotting the CMD on
    :param color_bar_ax: axes object where the color bar will go
    :param filters: list of filters the image was taken with
    :return: none. Figure and axes are modified in place
    """

    # first need to get the model's predictions_dict
    predictions_dict = models.make_prediction_dictionary(0.05)

    # Set the colormap, to color code lines by redshift
    spectral = plt.get_cmap("spectral")
    # Normalize the colormap so that the minimum value is the lowest color, and maximum is highest
    c_norm = mplcol.Normalize(vmin=min(predictions_dict), vmax=max(predictions_dict))
    scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=spectral)

    for z in predictions_dict:
        # Make the lines work with the plotting function. Rezip them from (x,y) pairs to x and y lists
        [xs, ys] = predictions_dict[z].rz_line
        # Get color
        color_val = scalar_map.to_rgba(predictions_dict[z].redshift)

        color_mag_ax.plot(xs, ys, color=color_val, linewidth=0.2)

        # Plot the points that correspond to L_star projected at those redshifts
        color_mag_ax.scatter(predictions_dict[z].z_mag,
                             predictions_dict[z].r_mag - predictions_dict[z].z_mag,
                             color=color_val)

    # Add a color bar
    scalar_map.set_array([])  # I don't know what this does, but I do know it needs to be here.
    fig.colorbar(scalar_map, cax=color_bar_ax)
    color_bar_ax.set_ylabel("Redshift")