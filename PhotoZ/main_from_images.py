from PhotoZ.files import SExtractor
from PhotoZ.files import functions
from PhotoZ.files import global_paths

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



# TODO: figure out how I want to handle catalogs of the same cluster but from different sources. IE my SE catalogs vs
#  the MaDCoWs catalogs I was given. Will probably do something with the filename, and then


# TODO: Good file system management. Have it save all data (catalogs, plots, etc) to the Astro folder,
# but copy important things to the GDrive.
# TODO: clean up Google Drive Data folder once this works

if START_WITH == 0:
    # Find all images in the desired directory. Will have a list of file paths.
    image_list = functions.find_all_objects(global_paths.images_directory, [".fits"], [])

    SExtractor.make_catalogs(image_list)


# if START_WITH <= 1:
#     functions.read_sextractor_catalogs(global_paths.catalogs_directory, [])