# Defines the function to create color-magnitude plots

import matplotlib.pyplot as plt
import os.path


def color_mag(color, mag, color_err=0, mag_err=0, title="Color Magnitude Diagram", x_label="z-band Magnitude",
              y_label="r-z Color", directory="/Users/gbbtz7/GoogleDrive/Research/Plots/", filename="", multipage=False):
    """ Make a color magnitude diagram and saves it in the directory specified.

    :param color: list of colors
    :param mag: list of magnitudes, must be same length as color
    :param color_err: list of errors in color. Must be same length as color and mag
    :param mag_err: list of errors in mag. Must be same length as all other lists
    :param title: Title the plot will be given. Naming it after the object may be nice.
    :param x_label: Label on x axis. Defaults to z band mag.
    :param y_label: Label on y axis. Defaults to r-z color.
    :param directory: Folder in which the plot will be saved. Defaults to the place I want mine saved.
    :param filename: Filename of the plot to be saved. Please include the ".pdf"
    :param multipage: Adds an identifiable string onto the title, so if you are producing multiple plots, you can later
           easily tell which ones need to be merges into one big .pdf
    """

    # Do some error checking
    # color and mag need to be same length
    if not len(color) == len(mag):
        print "The lengths color and mag are not the same length. Please try again"
        return 0
    # the directory they specified should exist
    if not os.path.exists(directory):
        print "Can't find that directory. Try again"
        return 0

    # If they didn't specify errors, assume zero. We need to make this into a list of zeros, so the lengths match
    if color_err == 0:
        color_err = []
        for i in range(len(color)):
            color_err.append(0)
    if mag_err == 0:
        mag_err = []
        for i in range(len(mag)):
            mag_err.append(0)


    # Need to ignore extraneous data points
    # Anything with a color above 5 or below -1 probably has something wrong with it
    for c in color:
        if c > 5 or c < -1:
            # remove the point from all the lists, after finding index
            index = color.index(c)
            color.pop(index)
            mag.pop(index)
            color_err.pop(index)
            mag_err.pop(index)

    # Everything should be set now, so we can go ahead and plot the figure, and set labels and all that stuff
    plt.figure(figsize=(6, 6))
    plt.scatter(mag, color, 10, c="k")
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)

    # If the user didn't provide a filename, make one
    if filename == "":
        if multipage:
            filename = title + "MERGE" + ".pdf"
        else:
            filename = title + ".pdf"

    # If the user didn't add .pdf, add it for them
    if not filename.endswith(".pdf"):
        filename += ".pdf"

    # Save the f
    plt.savefig(directory + filename, format='pdf')


    # STILL NEED TO INCORPORATE ERROR BARS!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!