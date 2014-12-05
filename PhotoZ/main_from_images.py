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
# note: selecting a lower number will still run everything after it. You may want to start at a later location, for
# example, if you've already read in catalogs and don't want to waste time doing it again. The code is smart enough to
# save it's progress after each step, so you don't need to worry about that.
START_WITH = 3

# TODO: run images through astrometry.net to correct astrometry.

# TODO: see if the color mag plot can be improved by chaning the way the colorbar is created. Rather than giving it its
# own axis, I would like it to steal from the other axis instead. That looks possible, so see if it works.

# initialize the resources file if it doesn't exist already.
try:
    open(global_paths.resources, "r")
except IOError:
    print "making new resources file"
    resources = open(global_paths.resources, "w")
    cPickle.dump(dict(), resources, -1)
    resources.close()

if START_WITH == 0:
    print "Starting SExtractor\n"
    # Find all images in the desired directory. Will have a list of file paths.
    image_list = functions.find_all_objects(global_paths.images_directory, [".fits"], [])

    # DOCUMENTED TO HERE

    SExtractor.sextractor_main(image_list)

    print "\nDone with SExtractor\n"

if START_WITH <= 1:
    print "\nStarted reading catalogs."
    cluster_list = read_in_catalogs.read_sex_catalogs()

    # Do color calculations
    for c in cluster_list:
        c.calculate_color()

    # save cluster list to disk
    pickle_file1 = open(global_paths.pickle_file, 'w')
    cPickle.dump(cluster_list, pickle_file1, -1)
    pickle_file1.close()

    print "\nDone reading catalogs\n"


if START_WITH == 2:
    # read in cluster objects
    pickle_file2 = open(global_paths.pickle_file, 'r')
    cluster_list = cPickle.load(pickle_file2)
    pickle_file2.close()

if START_WITH <= 2:
    print "\nStarting redshift fitting.\n"

    # find the red sequence redshifts
    for c in cluster_list:
        if c.r_data and c.z_data:
            c.fit_z("r-z", plot_figures=True)

    # save cluster list to disk
    pickle_file3 = open(global_paths.finished_pickle_file, 'w')
    cPickle.dump(cluster_list, pickle_file3, -1)
    pickle_file3.close()


if START_WITH == 3:
    cluster_list = cPickle.load(open(global_paths.finished_pickle_file, 'r'))

# fit a correction
functions.fit_correction(cluster_list, "r-z", read_in=False, plot=True)

# write results to a file
functions.write_results(cluster_list)

# TODO: look at clusters that calibration doens't work for. Use the crossID thing in SDSS to see if there really
# aren't stars there.



# TODO: make a function to calibrate catalogs to SDSS, rather than just starting from images. Can base it off of
# existing calibration function