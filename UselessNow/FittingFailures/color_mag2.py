# Defines the function that creates color-magnitude plots

import matplotlib.pyplot as plt


def make_color_mag_plot(galaxy_list, title="Color Magnitude Diagram",
                        directory="/Users/gbbtz7/GoogleDrive/Research/Plots/", filename="", multi_page=False):
    """Plot a color magnitude diagram, and save it as a pdf in the location specified. x,y axis labels come form the
    galaxy filters variable. The default values are what was convenient for me.

    :rtype : none
    :param galaxy_list: List of galaxy objects to be plotted on the CMD
    :param title: Title the plot will be given
    :param directory: Location the plot will be saved to. Defaults to the place I want mine saved.
    :param filename: Filename the plot will be saved with. If not given, will default to the title.pdf
           NOTE: Do not add .pdf to the end. The function will do that automatically
    :param multi_page: Adds an identifiable string onto the title, so if you are producing multiple plots, you can later
           easily tell which ones need to be merges into one big .pdf. If True, adds "MERGE", which is the default that
           the merge_pdf() function looks for.
    """

    # # Some galaxy objects have bad data, like color = 999. We need to remove these galaxies from our list
    # galaxy_list = [gal for gal in galaxy_list if gal.color < 5 and gal.color > -1]
    # galaxy_list = [gal for gal in galaxy_list if gal.color_error < 100]

    # Everything should be set now, so we can go ahead and plot the figure, and set labels and all that stuff
    plt.figure(figsize=(6, 6))
    # Need to iterate through galaxy_list to plot each point
    for gal in galaxy_list:
        plt.errorbar(x=gal.mag, y=gal.color, yerr=gal.color_error, c="k", fmt=".", elinewidth=.35, capsize=0,
                     markersize=5)
    plt.title(title)

    # Make x and y labels based on the filters this plot uses
    # All galaxies in the list use the same filters, so just look at the first one
    plt.xlabel(galaxy_list[0].filters[1] + " Band Magnitude")
    plt.ylabel(galaxy_list[0].filters[0] + " - " + galaxy_list[0].filters[1] + " Color")

    # Change the scale to match Stanford 14. Each filter set will be different
    if galaxy_list[0].filters[0] == "r":
        plt.xlim([20, 23.5])
        plt.ylim([0, 3.5])
    elif galaxy_list[0].filters[0] == "i":
        plt.xlim([18, 21.5])
        plt.ylim([-.5, 4.5])
    elif galaxy_list[0].filters[0] == "[3.6]":
        plt.xlim([18.5, 21.5])
        plt.ylim([-1, 0.5])

    # We need to make sure the filename works, and add the identifier if multi_page is specified
    # If they did specify a filename, and multi_page, add that
    if multi_page and filename != "":
        filename += "MERGE" + ".pdf"

    # If the user didn't provide a filename, make one
    if filename == "":
        if multi_page:  # use the default, which is "MERGE"
            filename = title + "MERGE" + ".pdf"
        else:  # No identifier needed
            filename = title + ".pdf"

    # If the user didn't add .pdf, add it for them
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    # Save the f
    plt.savefig(directory + filename, format='pdf')