
from PhotoZ.files import functions

# Tell the program where to start
# 0: will run everything. Starts with doing SExtractor in the images in the directory specified.
# 1: Starts by reading in catalogs, turning the different catalogs into Cluster objects
# 2: Starts by reading in saved Cluster objects from the specified directory.
# TODO: write better comments up here for where to start things, once I finishe the program.
START_WITH = 0



# Tell the program where the various things will be, so it can find them
# Directory containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
images_directory = "/Users/gbbtz7/Astro/Data/"
# Where SExtractor will be run from. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = "/Users/gbbtz7/Astro/SExtractor/"

#Where the SExtractor catalogs will be. The code will move the created files here, to reduce clutter in the
# SExtractor directory.
catalogs_directory = "/Users/gbbtz7/Astro/Data/SExtractorCatalogs/"
# TODO: write code to make sure each of these directories has a slash at the end.

if START_WITH == 0:
    # Find all images in the desired directory. Will have a list of file paths.
    image_list = functions.find_all_objects(images_directory, ".fits", [])
    for i in image_list:
        # We want to run SExtractor on all the images in a smart way.
        pass
if START_WITH <= 1:
    functions.read_sextractor_catalogs(catalogs_directory)