# Gillen Brown
# main_colormag.py - Attempts to recreate the color mag diagrams of Stanford 2014
from PhotoZ.files import plotting
from PhotoZ.files import main_functions


# read data in. read_data returns a list of cluster objects
clusters = main_functions.read_cluster_objects()

# Now we can make our plots, and put the figures into a list, to be saved later
figs = [plotting.plot_color_mag(cluster) for cluster in clusters]  # only use
#  r-z now

# Save the pdfs as one file
main_functions.save_as_one_pdf(figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/ColorMagPlots.pdf")