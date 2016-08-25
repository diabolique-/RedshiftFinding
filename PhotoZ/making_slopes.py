from PhotoZ import global_paths
from PhotoZ import config_data
import numpy.polynomial.polynomial as polynomial
import numpy as np
import matplotlib.pyplot as plt


def equivalent_redshift(coma_filter, distant_filter):
    """
    Find the distant redshift at which a given filter observing at that redshift will see the same rest frame as the
    given filter observing Coma.

    Used to find the redshifts at which the slope of the red sequence will be the same as in Eisenhardt 2007.

    :param coma_filter: filter that observed Coma
    :param distant_filte1: filter observing the distant object
    :return: redshift where the rest frame is equivalent for both filters

    Work on how I got this:
    The equivalent redshift is the redshift at which distant_filter is observing the same rest frame wavelength as
    coma_filter.

    1 + z = observed / emitted  [both are wavelengths]
    emitted = observed / (1 + z)  [where observed will be the effective wavelength of the filter used]

    For Coma:
    emitted = coma_filter / (1 + z_Coma)

    For distant object:
    1 + z = distant_filter / emitted
    Can now plug in the emitted wavelength from Coma (since we want effective to be the same for both)
    1 + z = distant_filter / (coma_filter / (1 + z_Coma))
    and rearrange
    z = {[distant_filter * (1 + z_Coma)] / coma_filter } - 1
    """

    return ((distant_filter * (1 + 0.023)) / coma_filter) - 1  # Since z_coma = 0.023


def make_all_equiv_z(colors, print_results=False):

    data_path = global_paths.home_directory + "/data/"
    # open the file containing Eisenhardt's filter's pivot wavelengths
    eisenhardt_file = open(data_path + "Eisenhardt2007_filters_pivot.txt", "r")

    # turn the filters from this file into a dictionary
    eisenhardt_filters = dict()
    for line in eisenhardt_file:
        if not line.startswith("#"):  # ignore comments
            eisenhardt_filters[line.split()[0]] = float(line.split()[1])
            # that dictionary will have keys=band names, values=pivot wavelength
    eisenhardt_file.close()

    # do the same thing with the filters that have cluster data
    filters_file = open(data_path + "filters.txt", "r")
    filters = dict()
    for line in filters_file:
        if not line.startswith("#"):
            filters[line.split()[0]] = float(line.split()[1])
            # that dictionary will have keys=band names, values=pivot wavelength
    filters_file.close()

    # open the file with the slopes from Eisenhardt's paper
    slopes_file = open(data_path + "rs_slopes.txt")
    # turn the slopes into a dictionary
    slopes = dict()
    for line in slopes_file:
        if not line.startswith("#"):
            slopes[line.split()[0]] = float(line.split()[1])
            # that dictionary will have keys=colors, values=slope of the red sequence in that color
    slopes_file.close()

    # now I can start the process of finding the function that will describe the slope of the red sequence as a
    # function of redshift
    slopes_at_redshifts = {color:[] for color in colors}
    for color in colors:
        # get the pivot wavelengths for the filters
        bluer_filter_wavelength = filters[color.split("-")[0]]
        redder_filter_wavelength = filters[color.split("-")[1]]
        for e_color in slopes:
            # get the pivot wavelength for eisenhardt's filters
            bluer_e_filter_wavelength = eisenhardt_filters[e_color.split("-")[0]]
            redder_e_filter_wavelength = eisenhardt_filters[e_color.split("-")[1]]

            # find the redshifts these two band pairs see each other
            bluer_pair_z = equivalent_redshift(bluer_e_filter_wavelength, bluer_filter_wavelength)
            redder_pair_z = equivalent_redshift(redder_e_filter_wavelength, redder_filter_wavelength)

            # if these are relatively close to each other, then the test pair is seeing Eisenhards's pair,
            # so we should keep track of the slope it sees at that redshift
            if 0.66 < bluer_pair_z/redder_pair_z < 1.5 and redder_pair_z > 0 and bluer_pair_z > 0:  #If they are
            # within a
            #  factor of
            # 1.5, it's close enough
                slopes_at_redshifts[color].append(((bluer_pair_z + redder_pair_z)/2.0, slopes[e_color]))
                # print color, e_color, (bluer_pair_z + redder_pair_z)/2.0
    # print slopes_at_redshifts








    # open the files with Eisenhardt and other filter pivot wavelengths
    data_path = global_paths.home_directory + '/data/'
    eisenhardt = open((data_path + "Eisenhardt2007_filters_pivot.txt"), "r")
    filters_file = open((data_path + "filters.txt"), "r")

    # Turn the filters into a dictionaries
    filters = dict()
    for line in eisenhardt:
        if not line.startswith("#"):
            filters[line.split()[0]] = float(line.split()[1])
    for line in filters_file:
        if not line.startswith("#"):
            filters[line.split()[0]] = float(line.split()[1])

    # close files
    eisenhardt.close()
    filters_file.close()


    #These are the filter pairs that will be used to calculate redshifts

    filter_redshifts = dict()  # intitialize empty dictionary to be filled

    for filter_pair in colors:

        shorter_filter_wavelength = filters[filter_pair.split("-")[0]]
        longer_filter_wavelength = filters[filter_pair.split("-")[1]]

       # find the redshift where the filter sees V-I
        first_VI_z = equivalent_redshift(filters["V"], shorter_filter_wavelength)
        second_VI_z = equivalent_redshift(filters["I"], longer_filter_wavelength)
        # since these redshifts won't be completely identical, average them to get an equivalent redshift
        VI_z = round(((first_VI_z + second_VI_z) / 2), 2)

        #find where filter pair sees B-R
        first_BR_z = equivalent_redshift(filters["B"], shorter_filter_wavelength)
        second_BR_z = equivalent_redshift(filters["R"], longer_filter_wavelength)
        # since these redshifts won't be completely identical, average them to get an equivalent redshift
        BR_z = round(((first_BR_z + second_BR_z) / 2), 2)

        # find the redshift where the filter sees U-V
        first_UV_z = equivalent_redshift(filters["U"], shorter_filter_wavelength)
        second_UV_z = equivalent_redshift(filters["V"], longer_filter_wavelength)
        # since these redshifts won't be completely identical, average them to get an equivalent redshift
        UV_z = round(((first_UV_z + second_UV_z) / 2), 2)

        if print_results:
            print(filter_pair)  # for debugging
            print first_VI_z, second_VI_z, VI_z
            print first_BR_z, second_BR_z, BR_z
            print first_UV_z, second_UV_z, UV_z

        filter_redshifts[filter_pair] = (VI_z, BR_z, UV_z)  # put the results into a dictionary


    return filter_redshifts





def make_slopes(colors):
    """
    Calculate the slope of the red sequence in different filter combinations.

    :param colors:strings that are filter combinations of the form [bluer filter]-[redder filter]. Check config_data.py
    for examples.
    :return:dictionary of keys=filter combinations and values=lambda functions describing the red sequence in that filter
        as a function of redshift. The given redshift will be input to the lambda function, and the slope of the red
        sequence will be returned.
    """

    # first get the equivalent redshifts
    color_equivalent_redshifts = make_all_equiv_z(colors, print_results=False)

    # here is the data from Eisenhardt 2007
    slopes = [-0.029, -0.055, -0.122] # in order of V-I, B-R, U-V
    # Make a list of known errors of slopes
    slope_errors = [0.005, 0.006, 0.01]
    #turn these errors into weights
    weights = [1/error for error in slope_errors]

    # initialize a dictionary that will be populated with lambda functions that describe the slope of the red sequence
    # as a function of redshift
    slope_dict = dict()

    for color in color_equivalent_redshifts:
        redshifts = color_equivalent_redshifts[color]

        # make the best fit line
        fit = polynomial.polyfit(redshifts, slopes, 1, w=weights)  # this returns 2 coefficients (first is constant,
        #  second is coefficient in front of x)

        # turn these coefficients into a dictionary
        slope_dict[color] = {str(round(z, 2)): fit[0] + z * fit[1] for z in np.arange(0, 3, 0.01)}

        # # now turn these fits into a line, if we want to plot to check for accuracy
        # x = np.arange(0, 10.0, 0.01)
        #
        # line = [slope_dict[color](z) for z in x]
        #
        # # # Plot points
        # plt.errorbar(redshifts, slopes, slope_errors, c="k", fmt=".", markersize=10, label="Data")
        # # Plot fit
        # plt.plot(x, line, "r--", label="Linear fit")
        # plt.legend(loc=0)
        # plt.xlabel("Redshift")
        # plt.ylabel("Slope of Red Sequence")
        # plt.suptitle("Slope of Red Sequence as a function of Redshift", fontsize=16)
        # plt.title(color, fontsize=12)
        # plt.show()
    return slope_dict
