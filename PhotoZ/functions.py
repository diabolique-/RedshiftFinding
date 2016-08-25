
from PhotoZ import plotting
from PhotoZ import global_paths
from PhotoZ import config_data
import os
import re
import math
import json
from matplotlib.backends.backend_pdf import PdfPages
import numpy.polynomial.polynomial as polynomial
import matplotlib.pyplot as plt
import cPickle


def find_all_objects(enclosing_directory, extensions, files_list):
    # DOCUMENTED
    """Recursively search the specified directory (and its subdirectories) for files that end in the desired extension.

    :param enclosing_directory: highest level directory containing the files
    :param extensions: List of possible extensions to be found.
    :type extensions: list of str
    :param files_list: list that the desired files will be appended to.
    :return: files_list, with the paths of all the files appended to it
    """




    # Make sure enclosing directory has a finishing /
    if not enclosing_directory.endswith("/"):
        enclosing_directory += "/"
    for f in os.listdir(enclosing_directory):
        entire_path = enclosing_directory + f
        # Determine if the item is a directory or not
        if os.path.isdir(entire_path):
            # If it is a directory, search through that directory with this function.
            find_all_objects(entire_path, extensions, files_list)
            # We don't need to record the output of the function, since the list we pass in will be modified in place.
        else:
            for ext in extensions:
                if entire_path.endswith(ext):
                    files_list.append(entire_path)

    return files_list
    # We technically don't need to return files_list, since changes in it will be reflected in the main program,
    # but often the user will just pass in an empty list without assigning it first. In this case, we need to return
    # something.





def make_cluster_name(filename):
    """Find the name of a cluster, based on its filename.

    Uses regular expressions to parse filenames, so I included lots of comments to try and explain what I'm doing here.

    :param filename: Filename that will be parsed into a cluster name.
    :type filename: str
    :return: name of the cluster
    :rtype: str
    """

    name = filename

    # First look for something of the form m####p####
    known_catalogs = re.compile("m[0-9]{4}(p|m)[0-9]{4}[.]phot[.]dat")
    # This means starts with an m, then 4 numeric characters, then p or m, then 4 more numeric characters

    my_catalog = re.compile(r"MOO[0-9]{4}([+]|[-])[0-9]{4}_sloan_(r|z)[.]cat")
    # This is the format my code outputs SExtractor catalogs with.

    gemini_images = re.compile(r"MOO[0-9]{4}([+]|[-])[0-9]{4}_(r|z)[.]fits")

    irac = re.compile(r"MOO_[0-9]{4}([+]|[-])[0-9]{4}_irac1_bg[.]fits[.]cat")
    # Format of IRAC catalogs. Has MOO_, 4 digits, + or -, 4 more digits, then _irac1_bg

    keck = re.compile(r"m[0-9]{4}(p|m)[0-9]{4}[.]zr[.]cat")

    if my_catalog.match(name):
        return name[0:12]  # Don't include band or extension
    elif gemini_images.match(name):
        return name[0:-7]  # Don't include band or extension
    elif irac.match(name):
        return "MOO" + name[4:13]  # MOO + the digits in the name
    elif known_catalogs.match(name):
        name = name[0:10]
        #  replace any p and m with + and - . I know I'm replacing the first m, but I will git rid of it next
        name = name.replace("p", "+")
        name = name.replace("m", "-")
        # Now have the beginning be taken off, and replaced with MOO.
        name = "MOO" + name[1:]
        # Append catalog to the name, so that I can distinguish these from the catalogs I made myself.
        # name += " catalog"
        return name

    elif keck.match(name):
        #  replace any p and m with + and - . I know I'm replacing the first m, but I will git rid of it next
        name = name.replace("p", "+")
        name = name.replace("m", "-")
        # Now have the beginning be taken off, and replaced with MOO.
        name = "MOO" + name[1:]

        return name[:-7]

    print name
    # TODO: Test other things, like the format of the IRAC catalogs, as well as a general case for something that does
    #  not match. IF it doesn't match, tell the user that.
    # TODO: add cases for Gemini images, as well as IRAC images.
    return "not working"


# TODO: delete this function? whould
# def get_band_from_filename(filename):
#     # DOCUMENTED
#     """Finds the band of an image or catalog based on the filename.
#
#     Assumes file names are of the form object_name_band.extension
#
#     :param filename: string with the filename
#     :return: string containing the band
#     """
#     file_no_extension = filename.split(".")[0]  # first thing before a .
#     band = file_no_extension.split("_")[-1]  # the band will be the last thing in the name itself
#     return band

def distance(x1, x2, y1, y2):
    """Uses the distance formula to calculate the distance between 2 objects
    dist = square root of the sum of the squared differences

    x and y are coordinates, so x1 and x2 are two values along one coordinate, and y1 and y2 are along the other.
    """
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def save_as_one_pdf(figs, filename):
    """
    Save the figures into one long PDF file

    :param figs: list of figures to be saved as PDFs
    :param filename: place where the PDFs will be saved
    :return: none
    """

    # Save the pdfs as one file
    pp = PdfPages(filename)
    for fig in figs:
        pp.savefig(fig)
    pp.close()
    for fig in figs:
        plt.close(fig)

def uJansky_to_AB_mag(uJanksys):
    # Convert to erg cm^-2 s^-1 Hz^-1, where 1 Jansky = 10^-23 erg cm^-2 s^-1 Hz^-1
    if uJanksys < 0.0:  # Some fluxes are negative, and that breaks the log function.
        return 9999999.9
    Janskys = uJanksys * (10**(-6))
    return -2.5*math.log10(Janskys) + 8.9
# AB to Vega: http://irsa.ipac.caltech.edu/data/COSMOS/tables/scosmos/scosmos_irac_200706_colDescriptions.html

def fit_corrections(cluster_list, read_in=False, plot=False):
    # TODO: document
    correction_path = global_paths.home_directory + "data/corrections.txt"
    figures = []
    fits = dict()
    if read_in:
        # read in the file with corrections
        correction_file = open(correction_path, "r")
        for line in correction_file.readlines():
            if not line.startswith("#"):
                color = line.split()[0]
                correction = json.loads(" ".join(line.split()[1:]))
                fits[color] = correction
        correction_file.close()
    else:
        for color in config_data.fitted_colors:
            spec_z_clusters = [c for c in cluster_list if c.spec_z and color in c.rs_z and not
                               c.name.startswith("MOO0224-0620")]  # throw out duplicates and one cluster with bad fit
            if len(spec_z_clusters) >= 1: # don't want to fit on too few data points

                spec_zs = [float(c.spec_z) for c in spec_z_clusters]
                rs_zs = [float(c.rs_z[color]) for c in spec_z_clusters]
                weights = [(1.0 / ((c.upper_photo_z_error[color] + c.lower_photo_z_error[color])/2))
                           for c in spec_z_clusters]
                # fit a function to the redshifts
                fits[color] = polynomial.polyfit(rs_zs, spec_zs, 1)#, w=weights)

        # save the corrections to disk
        correction_file = open(correction_path, "w")
        # json.dump(fits, correction_file)
        correction_file.write("{:17s} {:17s}\n".format("#color", "correction"))
        for color in fits:
            correction_file.write("{:17s} {:17s}\n".format(color, json.dumps(list(fits[color]))))
        correction_file.close()

    # correct the redshifts
    for color in fits:
        # Plot the redshifts pre-correction
        if plot:
            spec_z_clusters = [c for c in cluster_list if c.spec_z and color in c.rs_z and not
                               c.name.startswith("MOO0224-0620")]  # throw out duplicates and one cluster with bad fit

            figures.append(plotting.plot_z_comparison(spec_z_clusters, color, fits[color], label=False))

        # correct redshifts
        for c in cluster_list:
            if color in c.rs_z:
                measured_z = float(c.rs_z[color])
                corrected_z = 0
                # corrected z is a function of measured z, so we plug the observed value into the function
                for i in range(len(fits[color])):
                    corrected_z += fits[color][i]*measured_z**i
                c.rs_z[color] = str(round(corrected_z, 2))

        # plot the redshifts post-correction
        if plot:
            spec_z_clusters = [c for c in cluster_list if c.spec_z and color in c.rs_z and not
                               c.name.startswith("MOO0224-0620")]  # throw out duplicates and one cluster with bad fit

            figures.append(plotting.plot_z_comparison(spec_z_clusters, color, fit=None, label=False))

    # save the plots
    if plot:
        save_as_one_pdf(figures, global_paths.z_comparison_plots)







def write_results(clusters):
    # TODO: document
    # open file for writing
    f = open(global_paths.results, 'w')

    # write headings for the file
    f.write("{:23s} {:17s} {:5s} {:7s} {:7s} {:6s}\n".format("#cluster", "color", "z", "up err", "low err", "spec z"))

    for c in sorted(clusters, key=lambda c: c.name):  # sort clusters by name
        for color in c.rs_z:
            f.write("{:23s} {:17s} {:5s} {:7s} {:7s} {:6s}\n".format(c.name, color, c.rs_z[color],
                                                                  str(c.upper_photo_z_error[
                color]), str(c.lower_photo_z_error[color]), str(c.spec_z)))
    f.close()