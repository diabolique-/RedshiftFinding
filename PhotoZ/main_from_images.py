from PhotoZ.files import SExtractor
from PhotoZ.files import functions

# TODO: FIGURE OUT WHAT A MAIN IS IN PYTHON, AND IMPLEMENT THAT TOO. I WANT THIS TO BE A MODULE.

# Tell the program where to start
# 0: will run everything. Starts with doing SExtractor in the images in the directory specified.
# 1: Starts by reading in catalogs, turning the different catalogs into Cluster objects
# 2: Starts by reading in saved Cluster objects from the specified directory.
# TODO: write better comments up here for where to start things, once I finish the program.
START_WITH = 0

# TODO: run images through astrometry.net to correct astrometry.

# tODO: make it capable of calling sources in the red sequence, even if they are outside the radius cut I do to
# select the cluster.

# Tell the program where the various things will be, so it can find them
# Directory containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
# I call the function to ensure there is a slash at the end of the directory.
images_directory = functions.check_for_slash("/Users/gbbtz7/Astro/RS_finding/Data/Images/Gemini/Corrected/")

# Where SExtractor will be run from. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = functions.check_for_slash("/Users/gbbtz7/Astro/SExtractor/")


# Where the SExtractor catalogs will be. The code will move the created files here, to reduce clutter in the
# SExtractor directory.
catalogs_directory = functions.check_for_slash("/Users/gbbtz7/Astro/RS_finding/Data/Catalogs/Gemini/")


# All these variables that hold file locations will be called as global variables from within functions,
# just so I don't have to waste time passing all them around. It would be a mess.


# TODO: figure out how I want to handle catalogs of the same cluster but from different sources. IE my SE catalogs vs
#  the MaDCoWs catalogs I was given. Will probably do something with the filename, and then


# TODO: Good file system management. Have it save all data (catalogs, plots, etc) to the Astro folder,
# but copy important things to the GDrive.
# TODO: clean up Google Drive Data folder once this works

if START_WITH == 0:
    # Find all images in the desired directory. Will have a list of file paths.
    image_list = functions.find_all_objects(images_directory, [".fits"], [])

    SExtractor.make_catalogs(image_list)


if START_WITH <= 1:
    functions.read_sextractor_catalogs(catalogs_directory, [])