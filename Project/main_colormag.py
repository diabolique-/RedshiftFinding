# Gillen Brown
# main_colormag.py - Attempts to recreate the color mag diagrams of Stanford 2014
from Project.files import plotting
from Project.files import main_functions


# read data in. read_data returns a list of image objects
images = main_functions.read_image_objects()

# Only use r-z ones for now
images = [i for i in images if i.filters == ["r", "z"]]

# Now we can make our plots, and put the figures into a list, to be saved later
# figs = [plotting.plot_color_mag(image, predictions=True) for image in images]
figs = []
for image in images:
    fig, ax = plotting.plot_color_mag(image, predictions=True)
    figs.append(fig)

# Save the pdfs as one file
main_functions.save_as_one_pdf(figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/ColorMagPlots.pdf")