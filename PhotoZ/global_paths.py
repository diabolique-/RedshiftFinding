import os

# Tell the program where the various things will be, so it can find them
# DO NOT FORGET A SLASH ON THINGS THAT ARE SUPPOSED TO BE DIRECTORIES!!

# define a base directory, so you don't have to type the same thing each time
# base_directory = "/Users/gbbtz7/"
base_directory = "/Users/gillenbrown/"

#this will return the directory of the module itself. DO NOT CHANGE THIS LINE
home_directory = os.path.dirname(os.path.realpath(__file__)) + "/"  # DO NOT CHANGE.

########################################################################################################################

##   Source Extractor/Images

########################################################################################################################
# Directories containing all the images. They can be in subdirectories of this directory; it will find all .fits files
# in this directory.
images_directory = [base_directory + "Astro/RS_finding/Data/Images/Gemini/Corrected/"]

# SExtractor will run from here. This directory should hold the .sex and .param files that SExtractor uses
sextractor_params_directory = base_directory + "GoogleDrive/Research/SExtractor_files/"

# Config files sextractor will use for different bands
gemini_config_file = sextractor_params_directory + "gemini.sex"

# Directory where the SExtractor catalogs will be saved to. The code will move the created files here, to reduce clutter
#  in the SExtractor directory.
catalogs_save_directory = base_directory + "GoogleDrive/Research/Data/Catalogs/Gemini/"

########################################################################################################################

## Catalogs

########################################################################################################################

# Directory where the code will look for all catalogs. Will search in all subdirectories, like the image search. Don't
# forget to include the directory where the SExtractor catalogs were saved.
catalogs_look_directory = base_directory + "GoogleDrive/Research/Data/Catalogs/"

# Directory for calibration catalogs to be saved to.
calibration_catalogs_directory = base_directory + "GoogleDrive/Research/Data/SDSS_catalogs"

########################################################################################################################

## Results

########################################################################################################################
# file to save calibration plots
calibration_plots = base_directory + "GoogleDrive/Research/Plots/calibration.pdf"

# directory to save plots of the redshift fitting process. Each cluster will get its own file.
plots = base_directory + "GoogleDrive/Research/Plots/ClusterFitting/"

# directory to save redshift comparison plots, showing how the redshift correction function was obtained.
z_comparison_plots = base_directory + "GoogleDrive/Research/Plots/z.pdf"

# file to save the resulting .txt file with redshifts to
results = base_directory + "GoogleDrive/Research/Plots/results.txt"

# directory to store resulting catalogs of sources that are or are not RS members
rs_catalogs = base_directory + "GoogleDrive/Research/Data/RS_catalogs/"



########################################################################################################################

## Other

########################################################################################################################

# File that will be used to store miscellanous data the program calculates and wants to save
resources = home_directory + "data/resources.p"

# directory to store RS slopes. W# TODO: consolidate this into one thing with other various data
rs_slopes = base_directory + "GoogleDrive/Research/Data/CodeData/Best_fit_RS_slope.pickle"

# Place to store Python saved objects. Clusters will be pickled to this location.
pickle_file = base_directory + "GoogleDrive/Research/Data/CodeData/PythonSavedClusters/Clusters.p"
finished_pickle_file = base_directory + "GoogleDrive/Research/Data/CodeData/PythonSavedClusters/FinishedClusters.p"

# All these variables that hold file locations will be called as global variables from within functions,
# just so I don't have to waste time passing all them around. It would be a mess.