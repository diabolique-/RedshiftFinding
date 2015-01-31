# Gillen Brown
# Attempt1.py - Attempts to recreate the color mag diagrams of Stanford 2014

import color_mag1
import os
from PyPDF2 import PdfFileMerger, PdfFileReader


# Iterate through all the data files, and make color mag plots for them
for file in os.listdir("/Users/gbbtz7/GoogleDrive/Research/Data/madcows.specz.phot"):
    if file.endswith(".dat"):  # not all files are what we want
        # open the f
        data_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/madcows.specz.phot/" + file, "r")

        # Then read the data in in a readable way
        # I'll start with an empty list, then populate it as the f is read in
        data = []
        for line in data_file:
            if not line.startswith("#"):
                data.append(line.split())  # Use split to break the line elements up
        # After reading in, the variable data will be a list of lists, where the larger list is a list of objects, and
        # the inner lists are the different attrbutes
        # the small lists are in this order [id, ra, dec, mag, color, color_error]

        print file # for debugging purposes

        # Need to reshape the data to make it fit the plot_color_mag function
        color = [float(data[i][4]) for i in range(len(data))]
        mag = [float(data[i][3]) for i in range(len(data))]
        #color_err = [float(data[i][5]) for i in range(len(data))]  # Something wrong with this line

        # Pass things to the plot_color_mag function to plot them
        color_mag1.color_mag(color,mag,title=file[0:-9], multipage=True) # Don't want the .phot.dat in the name


# we created multiple plots, so merge them together
merger = PdfFileMerger()
for pdf in os.listdir("/Users/gbbtz7/GoogleDrive/Research/Plots"):
    if pdf.endswith("MERGE.pdf"):  # the MERGE is from specifying multipage=True in the plot_color_mag function
        # Open and append the f
        opened_pdf = open("/Users/gbbtz7/GoogleDrive/Research/Plots/" + pdf, "rb")
        merger.append(opened_pdf)
        # remove the files we merged into one, to remove clutter, after closing
        opened_pdf.close()
        os.remove("/Users/gbbtz7/GoogleDrive/Research/Plots/" + pdf)

# Now write the combined .pdf
merger.write("/Users/gbbtz7/GoogleDrive/Research/Plots/ColorMagPlots.pdf")



