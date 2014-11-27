

# TODO: document this better

def check_for_slash(path):
    """Check the given directory for a slash at the end. If it doesn't have one, add it.

    :param path: Path to be checked for a slash.
    :type path: str
    :return: corrected path
    :rtype: str
    """
    if path.endswith("/"):
        return path
    else:
        return path + "/"

# base_directory = "/Users/gbbtz7/"
base_directory = "/Users/gillenbrown/"

# TODO: organize these things. They are all over the place

# Tell the program where the various things will be, so it can find them
# Directory containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
# I call the function to ensure there is a slash at the end of the directory.
images_directory = check_for_slash(base_directory + "Astro/RS_finding/Data/Images/Gemini/Corrected/")

# SExtractor will run from here. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = check_for_slash(base_directory + "GoogleDrive/Research/SExtractor_files/")
# Config files sextractor will use for different bands
gemini_config_file = sextractor_params_directory + "gemini.sex"


# Where the SExtractor catalogs will be. The code will move the created files here, to reduce clutter in the
# SExtractor directory.
catalogs_save_directory = check_for_slash(base_directory + "GoogleDrive/Research/Data/Catalogs/Gemini/")

#Where the code will look for all catalogs. Needs to be either the same directory as catalogs_save_directory,
# or a parent directory of it.

# catalogs_look_directory = functions.check_for_slash("/Users/gbbtz7/GoogleDrive/Research/Data/Catalogs/")
catalogs_look_directory = check_for_slash("/Users/gbbtz7/GoogleDrive/Research/Data/Catalogs/")

# catalogs_look_directory = functions.check_for_slash("/Users/gbbtz7/GoogleDrive/Research/Data/Catalogs/IRAC/")
# catalogs_look_directory = functions.check_for_slash("/Users/gbbtz7/GoogleDrive/Research/Data/Catalogs/tes1/")


# Location for calibration catalogs to be saved to.
calibration_catalogs_directory = check_for_slash(base_directory + "GoogleDrive/Research/Data/SDSS_catalogs")

# Place to store Python saved objects. Clusters will be pickled to this location.
pickle_file = base_directory + "GoogleDrive/Research/Data/CodeData/PythonSavedClusters/Clusters.p"
finished_pickle_file = base_directory + "GoogleDrive/Research/Data/CodeData/PythonSavedClusters/FinishedClusters.p"

# Place to save calibration plots
calibration_plots = base_directory + "GoogleDrive/Research/Plots/calibration.pdf"

# Place to save redshift comparison plots
z_comparison_plots = base_directory + "GoogleDrive/Research/Plots/z.pdf"

# Place to save all other plots
plots = base_directory + check_for_slash("GoogleDrive/Research/Plots/ClusterFitting/")

# Place to save the correction
correction_location = base_directory + "GoogleDrive/Research/Data/CodeData/correction.p"

# location to save the resulting .txt file with redshifts to
results = base_directory + "GoogleDrive/Research/Plots/results.txt"

# Place to store resulting catalogs of sources that are or are not RS members
rs_catalogs = check_for_slash(base_directory + "GoogleDrive/Research/Data/RS_catalogs/")

# place to store RS slopes. W# TODO: consolidate this into one thing with other various data
rs_slopes = base_directory + "GoogleDrive/Research/Data/CodeData/Best_fit_RS_slope.pickle"

initial_z_plots = base_directory + "GoogleDrive/Research/Plots/InitialZ/"

# All these variables that hold file locations will be called as global variables from within functions,
# just so I don't have to waste time passing all them around. It would be a mess.