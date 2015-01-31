# Defines the function that creates color-magnitude plots

import matplotlib.pyplot as plt



def make_color_mag_plot(galaxy_list, title="Color Magnitude Diagram", histogram=False, model_prediction=False):
    """Plot a color magnitude diagram, and save it as a pdf in the location specified. x,y axis labels come form the
    galaxy filters variable. The default values are what was convenient for me.

    :rtype : figure
    :param galaxy_list: List of galaxy objects to be plotted on the CMD
    :param histogram: Whether or not to make a color histogram as well.
    :param model_prediction: Whether or not to include predictions of color from EzGal models
    """

    # The axes need to be set up differently if we want a histogram
    if histogram:
        # Get the axes set up
        fig = plt.figure(figsize=(9, 6))
        gs = plt.GridSpec(1, 2, width_ratios=[4, 1], wspace=0.01)

        color_mag_ax = plt.subplot(gs[0, 0])
        histogram_ax = plt.subplot(gs[0, 1])

        # Call the function to plot the histogram
        add_histogram(galaxy_list, histogram_ax)

    else:  # No histogram
        # Set up the axes
        fig = plt.figure(figsize=(6, 6))
        color_mag_ax = fig.add_subplot(1, 1, 1)

    # Need to iterate through galaxy_list to plot each point on the CMD
    for gal in galaxy_list:
        color_mag_ax.errorbar(x=gal.mag, y=gal.color, yerr=gal.color_error, c="k", fmt=".", elinewidth=.35, capsize=0,
                              markersize=5)

    color_mag_ax.set_title(title)

    # Make x and y labels based on the filters this plot uses
    # All galaxies in the list use the same filters, so just look at the first one
    color_mag_ax.set_xlabel(galaxy_list[0].filters[1] + " Band Magnitude")
    color_mag_ax.set_ylabel(galaxy_list[0].filters[0] + " - " + galaxy_list[0].filters[1] + " Color")

    # Change the scale to match Stanford 14. Each filter set will be different
    if galaxy_list[0].filters[0] == "r":
        color_mag_ax.set_xlim([20, 23.5])
        color_mag_ax.set_ylim([0, 3.5])
    elif galaxy_list[0].filters[0] == "i":
        color_mag_ax.set_xlim([18, 21.5])
        color_mag_ax.set_ylim([-.5, 4.5])
    elif galaxy_list[0].filters[0] == "[3.6]":
        color_mag_ax.set_xlim([18.5, 21.5])
        color_mag_ax.set_ylim([-1, 0.5])

    # If model predictions are wanted, plot those now
    if model_prediction:
        fig = plot_predictions(fig, color_mag_ax, galaxy_list[0].filters[0])

    return fig