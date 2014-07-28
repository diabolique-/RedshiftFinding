
from UselessNow.NotFromImages import main_functions
# Tell the program where the various things will be, so it can find them
# Directory containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
images_directory = "/Users/gbbtz7/Astro/Data/"
# Where SExtractor will be run from. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = "/Users/gbbtz7/Astro/SExtractor/"

# TODO: set variables for where the program will start. I don't want to run SExtractor each time this program runs.

# Find all images in the desired directory. Will have a list of file paths.
image_list = main_functions.find_all_objects(images_directory, ".fits", [])
for i in image_list:
    print i

