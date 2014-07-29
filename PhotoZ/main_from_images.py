
from PhotoZ.files import functions

# Tell the program where to start
# 0: will run everything. Starts with doing SExtractor in the images in the directory specified.
# 1: Starts by reading in catalogs, turning the different catalogs into Cluster objects
# 2: Starts by reading in saved Cluster objects from the specified directory.
# TODO: write better comments up here for where to start things, once I finish the program.
START_WITH = 0

# TODO: run images through astrometry.net to correct astrometry.

# Tell the program where the various things will be, so it can find them
# Directory containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
images_directory = "/Users/gbbtz7/Astro/Data/Images/gem/"  # Don't forget / !!!!!

# Where SExtractor will be run from. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = "/Users/gbbtz7/Astro/SExtractor/"  # Don't forget / !!!!!


#Where the SExtractor catalogs will be. The code will move the created files here, to reduce clutter in the
# SExtractor directory.
catalogs_directory = "/Users/gbbtz7/Astro/Data/SExtractorCatalogs/"  # Don't forget / !!!!!


# All these variables that hold file locations will be called as global variables from within functions,
# just so I don't have to waste time passing all them around. It would be a mess.


# TODO: figure out an elegant way to ensure that all directories have a slash at the end.


# TODO: Good file system management. Have it save all data (catalogs, plots, etc) to the Astro folder,
# but copy important things to the GDrive. That will make my code simpler (since I

if START_WITH == 0:
    # Find all images in the desired directory. Will have a list of file paths.
    image_list = functions.find_all_objects(images_directory, ".fits", [])
    for i in image_list:
        # We want to run SExtractor on all the images in a smart way.
        pass
if START_WITH <= 1:
    functions.read_sextractor_catalogs(catalogs_directory, [])