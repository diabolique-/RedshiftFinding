from PhotoZ.files import functions

# TODO: document this better
# Tell the program where the various things will be, so it can find them
# Directory containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
# I call the function to ensure there is a slash at the end of the directory.
images_directory = functions.check_for_slash("/Users/gbbtz7/Astro/RS_finding/Data/Images/Gemini/Corrected/")

# Where SExtractor will be run from. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = functions.check_for_slash("/Users/gbbtz7/Astro/SExtractor/")
# Config files sextractor will use for different bands
config_file = sextractor_params_directory + "gemini.sex"

# Where the SExtractor catalogs will be. The code will move the created files here, to reduce clutter in the
# SExtractor directory.
catalogs_directory = functions.check_for_slash("/Users/gbbtz7/Astro/RS_finding/Data/Catalogs/Gemini/")

# All these variables that hold file locations will be called as global variables from within functions,
# just so I don't have to waste time passing all them around. It would be a mess.
