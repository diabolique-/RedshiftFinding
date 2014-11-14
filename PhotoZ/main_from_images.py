from PhotoZ.files import SExtractor
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import read_in_catalogs
import cPickle


# Tell the program where to start
# 0: will run everything. Starts with doing SExtractor in the images in the directory specified.
# 1: Starts by reading in catalogs, turning the different catalogs into Cluster objects
# 2: Starts by reading in saved Cluster objects from the specified directory.
# 3: Starts by reading in saved Cluster list after it has finished, so they all have redshifts. There is still the
#       correction to be done.
# TODO: write better comments up here for where to start things, once I finish the program.
START_WITH = 2

# TODO: run images through astrometry.net to correct astrometry.

if START_WITH == 0:
    print "Starting SExtractor\n"
    # Find all images in the desired directory. Will have a list of file paths.
    image_list = functions.find_all_objects(global_paths.images_directory, [".fits"], [])

    SExtractor.sextractor_main(image_list)

    print "\nDone with SExtractor\n"

if START_WITH <= 1:
    print "\nStarted reading catalogs."
    cluster_list = read_in_catalogs.read_sex_catalogs()

    # Do color calculations
    for c in cluster_list:
        c.calculate_color()

    # save cluster list to disk
    cPickle.dump(cluster_list, open(global_paths.pickle_file, 'w'), -1)

    print "\nDone reading catalogs\n"


if START_WITH == 2:
    # read in cluster objects
    cluster_list = cPickle.load(open(global_paths.pickle_file, 'r'))

if START_WITH <= 2:
    print "\nStarting redshift fitting.\n"

    # find the red sequence redshifts
    for c in cluster_list:
        if c.r_data and c.z_data:
            c.fit_z("r-z", plot_figures=True)

    # save cluster list to disk
    cPickle.dump(cluster_list, open(global_paths.finished_pickle_file, 'w'), -1)
    # TODO: save each plot individually after it is done. I don't want a huge list anymore.

if START_WITH == 3:
    cluster_list = cPickle.load(open(global_paths.finished_pickle_file, 'r'))

# fit a correction
functions.fit_correction(cluster_list, "r-z", plot=True)

# write results to a file
functions.write_results(cluster_list)

# TODO: look at clusters that calibration doens't work for. Use the crossID thing in SDSS to see if there really
# aren't stars there.



# TODO: make a function to calibrate catalogs to SDSS, rather than just starting from images. Can base it off of
# existing calibration function