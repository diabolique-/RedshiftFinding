from PhotoZ.files import SExtractor
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import read_in_catalogs
import cPickle


# Tell the program where to start
# 0: will run everything. Starts with doing SExtractor in the images in the directory specified.
# 1: Starts by reading in catalogs, turning the different catalogs into Cluster objects
# 2: Starts by reading in saved Cluster objects from the specified directory.
# TODO: write better comments up here for where to start things, once I finish the program.
START_WITH = 1

# TODO: run images through astrometry.net to correct astrometry.

# tODO: make it capable of calling sources in the red sequence, even if they are outside the radius cut I do to
# select the cluster.



# TODO: figure out how I want to handle catalogs of the same cluster but from different sources. IE my SE catalogs vs
#  the MaDCoWs catalogs I was given. Will probably do something with the filename, and then


if START_WITH == 0:
    # Find all images in the desired directory. Will have a list of file paths.
    image_list = functions.find_all_objects(global_paths.images_directory, [".fits"], [])

    SExtractor.sextractor_main(image_list)

    print "\n\nDone with SExtractor\n\n"

if START_WITH <= 1:
    cluster_list = read_in_catalogs.read_sex_catalogs()

    # Do color calculations
    for c in cluster_list:
        c.calculate_color()

    # save cluster list to disk
    cPickle.dump(cluster_list, open(global_paths.pickle_file, 'w'), -1)

    print "\n\nDone reading catalogs\n\n"


if START_WITH == 2:
    # read in cluster objects
    cluster_list = cPickle.load(open(global_paths.pickle_file, 'r'))

if START_WITH <= 2:
    # for c in cluster_list:
    #     for s in c.sources_list:
    #         print s.mags, s.colors
    figs = []
    # find the red sequence redshifts
    figures = [c.fit_z("r-z", plot_figures=figs) for c in cluster_list if c.r_data and c.z_data]
    functions.save_as_one_pdf(figs, global_paths.plots)
     # Do color calculations
    # for c in cluster_list:
    #     c.calculate_color()