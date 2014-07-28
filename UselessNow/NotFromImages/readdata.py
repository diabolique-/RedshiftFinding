import os
import os.path as path
import cPickle

from UselessNow.NotFromImages import other_classes
from UselessNow.NotFromImages import Cluster


def make_data_list(directory, paths_list):
    """ Recursively find all the data files in the directory, and append their path to the list, which is returned.

    :param directory: Directory where the data files are. Can have folders within this folder with other data.
    :param paths_list: List of paths that will be searched for data files.
    :return: List of paths that point to data files.
    """
    for f in os.listdir(directory):
        # Want whole path information, not just filename
        full_path = directory + "/" + f
        # For directories, we want to search them for files too. Recursively call this function to do that.
        if path.isdir(full_path):
            make_data_list(full_path, paths_list)
            # If it's a file, we only want data files
        elif full_path.endswith(".dat"):
            paths_list.append(full_path)
    return paths_list


images = []

# Create a dictionary mapping the objects to their known redshifts, for assigning to image objects
redshifts = {"m0012p1602.phot.dat": "0.94", "m0024p3303.phot.dat": "1.11", "m0125p1344.phot.dat": "1.12",
             "m0130p0922.phot.dat": "1.15", "m0133m1057.phot.dat": "0.96", "m0212m1813.phot.dat": "1.09",
             "m0224m0620.phot.dat": "0.81", "m0245p2018.phot.dat": "0.76", "m0319m0025.phot.dat": "1.19",
             "m1155p3901.phot.dat": "1.01", "m1210p3154.phot.dat": "1.05", "m1319p5519.phot.dat": "0.94",
             "m1335p3004.phot.dat": "0.98", "m1514p1346.phot.dat": "1.06", "m1625p2629.phot.dat": "1.20",
             "m2205m0917.phot.dat": "0.93", "m2320m0620.phot.dat": "0.92", "m2348p0846.phot.dat": "0.89",
             "m2355p1030.phot.dat": "1.27"}

# Find all the data files in the directory
files_list = make_data_list("/Users/gbbtz7/GoogleDrive/Research/Data/ClusterData", [])

# Iterate through all the data files, and save the data to an image object
for file_path in files_list:
    file_name = file_path.split("/")[-1]
    # Parse the filename (which is the object's name) into a good image name
    name = file_name[1: -9]  # Exclude the beginning m, and the extensions on the end. This leaves the object name
    # Parse the rest to add the + or - in the correct spot
    name = name.replace("m", "-")
    name = name.replace("p", "+")
    #Add MOO on the front
    name = "MOO" + name
# TODO: MAke this work for arbitrary catalogs
    # open the file
    data_file = open(file_path, "r")

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
    if file_name in redshifts:
        image = Cluster.Cluster([], name, filters, redshifts[file_name])
    else:
        image = Cluster.Cluster([], name, filters)

    # Then go through and find the data
    for line in data_file:
        if not line.startswith("#"):  # We don't want the commented lines
            # Split the line into the attributes, and temporarily store it
            data_line = line.split()
            # Data line will now be a list with elements [id, ra, dec, mag, color, color error]

            # Now make the galaxy object, and append it to my list of galaxy objects
            # Sometimes the data files don't have an ID, so we need to be aware of that
            if len(data_line) == 6:  # If there is an ID
                image.galaxy_list.append(other_classes.Galaxy(id_num=data_line[0], ra=data_line[1],
                                                              dec=data_line[2], mag=data_line[3],
                                                              color=data_line[4], color_error=data_line[5]))

            else:  # If there is not an ID (only happens in m0245p2018.phot.dat)
                image.galaxy_list.append(other_classes.Galaxy(id_num=-999, ra=(data_line[0]), dec=data_line[1],
                                                              mag=data_line[2], color=data_line[3],
                                                              color_error=data_line[4]))
    images.append(image)

    # close the file
    data_file.close()

# We now have a list of clusters. We can save these to disk using the cPickle module
for i in images:
    cPickle.dump(i, open("/Users/gbbtz7/GoogleDrive/Research/Data/PythonSavedClusters/" + i.name + ".p", "w"), -1)