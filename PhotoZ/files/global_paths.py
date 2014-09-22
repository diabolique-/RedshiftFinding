from PhotoZ.files import functions

# TODO: document this better

# Tell the program where the various things will be, so it can find them
# Directory containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
# I call the function to ensure there is a slash at the end of the directory.
images_directory = functions.check_for_slash("/Users/gbbtz7/Astro/RS_finding/Data/Images/Gemini/Corrected/")

# SExtractor will run from here. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = functions.check_for_slash("/Users/gbbtz7/GoogleDrive/Research/SExtractor_files/")
# Config files sextractor will use for different bands
r_config_file = sextractor_params_directory + "r.sex"
z_config_file = sextractor_params_directory + "z.sex"


# Where the SExtractor catalogs will be. The code will move the created files here, to reduce clutter in the
# SExtractor directory.
catalogs_save_directory = functions.check_for_slash("/Users/gbbtz7/GoogleDrive/Research/Data/Catalogs/Gemini/")

#Where the code will look for all catalogs. Needs to be either the same directory as catalogs_save_directory,
# or a parent directory of it.
catalogs_look_directory = functions.check_for_slash("/Users/gbbtz7/GoogleDrive/Research/Data/Catalogs/")

# Location for calibration catalogs to be saved to.
calibration_catalogs_directory = functions.check_for_slash("/Users/gbbtz7/GoogleDrive/Research/Data/SDSS_catalogs")

# Place to store Python saved objects. Clusters will be pickled to this location.
pickle_file = "/Users/gbbtz7/GoogleDrive/Research/Data/CodeData/PythonSavedClusters/Clusters.p"

# Place to save calibration plots
calibration_plots = "/Users/gbbtz7/GoogleDrive/Research/Plots/calibration.pdf"

# Place to save all other plots
plots = "/Users/gbbtz7/GoogleDrive/Research/Plots/Complete.pdf"

# All these variables that hold file locations will be called as global variables from within functions,
# just so I don't have to waste time passing all them around. It would be a mess.