import os
import cPickle
from PhotoZ.files import classes

# Reads the data in from the file, turns it into objects, and saves it so it can be used later



images = []

# Create a dictionary mapping the objects to their known redshifts, for assigning to image objects
redshifts = {"m0012p1602.phot.dat": "0.94", "m0024p3303.phot.dat": "1.11", "m0125p1344.phot.dat": "1.12",
             "m0130p0922.phot.dat": "1.15", "m0133m1057.phot.dat": "0.96", "m0212m1813.phot.dat": "1.09",
             "m0224m0620.phot.dat": "0.81", "m0245p2018.phot.dat": "0.76", "m0319m0025.phot.dat": "1.19",
             "m1155p3901.phot.dat": "1.01", "m1210p3154.phot.dat": "1.05", "m1319p5519.phot.dat": "0.94",
             "m1335p3004.phot.dat": "0.98", "m1514p1346.phot.dat": "1.06", "m1625p2629.phot.dat": "1.20",
             "m2205m0917.phot.dat": "0.93", "m2320m0620.phot.dat": "0.92", "m2348p0846.phot.dat": "0.89",
             "m2355p1030.phot.dat": "1.27"}

# Iterate through all the data files, and save the data to an image object
for f in os.listdir("/Users/gbbtz7/GoogleDrive/Research/Data/madcows.specz.phot/"):
    if f.endswith(".dat"):  # not all files are what we want

        # Parse the filename (which is the object's name) into a good image name
        name = f[1: -9]  # Exclude the beginning m, and the extensions on the end. This leaves the object name
        # Parse the rest to add the + or - in the correct spot
        name = name.replace("m", "-")
        name = name.replace("p", "+")
        #Add MOO on the front
        name = "MOO" + name

        # open the file
        data_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/madcows.specz.phot/" + f, "r")

        # first line contains the info about the filters used
        data_categories = data_file.readline().split()
        # use that info to figure out which this image is using
        if data_categories[5] == "rmz":  # data_categories[5] is where the color is stored, and it tells both filters
            filters = ["r", "z"]
        elif data_categories[5] == "imch1":
            filters = ["i", "[3.6]"]
        elif data_categories[5] == "ch1mch2":
            filters = ["[3.6]", "[4.5]"]
        else:
            filters = ["something else"]

        # Initialize an image object, with empty list of galaxies. Will append to that as we read data in
        image = classes.Image([], name, filters, redshifts[f])

        # Then go through and find the data
        for line in data_file:
            if not line.startswith("#"):  # We don't want the commented lines
                # Split the line into the attributes, and temporarily store it
                data_line = line.split()
                # Data line will now be a list with elements [id, ra, dec, mag, color, color error]

                # Now make the galaxy object, and append it to my list of galaxy objects
                # Sometimes the data files don't have an ID, so we need to be aware of that
                if len(data_line) == 6:  # If there is an ID
                    image.galaxy_list.append(classes.Galaxy(id_num=data_line[0], ra=data_line[1], dec=data_line[2],
                                                            mag=data_line[3], color=data_line[4],
                                                            color_error=data_line[5]))

                else:  # If there is not an ID (only happens in m0245p2018.phot.dat)
                    image.galaxy_list.append(classes.Galaxy(id_num=-999, ra=(data_line[0]), dec=data_line[1],
                                                            mag=data_line[2], color=data_line[3],
                                                            color_error=data_line[4]))

        images.append(image)

        # close the file
        data_file.close()
print images

# We now have a list of images. We can save these to disk using the cPickle module
cPickle.dump(images, open("/Users/gbbtz7/GoogleDrive/Research/Data/images.pickle", "w"), -1)