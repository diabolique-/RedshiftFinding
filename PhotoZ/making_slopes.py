import os
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
    Can now plug in the emitted wavelength from Coma
    1 + z = distant_filter / (coma_filter / (1 + z_Coma))
    and rearrange
    z = {[distant_filter * (1 + z_Coma)] / coma_filter } - 1
    """

    return ((distant_filter * (1 + 0.023)) / coma_filter) - 1  # Since z_coma = 0.023


def make_all_equiv_z():

    # open the files with Eisenhardt and other filter pivot wavelengths
    eisenhardt = open("/Users/gillenbrown/GoogleDrive/Research/Data/CodeData/Eisenhardt2007filters_effective.dat", "r")
    # TODO: make these paths part of the package, rahter than be stored elsewhere
    filters_file = open("/Users/gillenbrown/GoogleDrive/Research/Data/CodeData/filters.txt", "r")

    # Turn the filters into a dictionaries
    filters = dict()
    for line in eisenhardt:
        if not line.startswith("#"):
            filters[line.split()[0]] = float(line.split()[1])
    for line in filters_file:
        if not line.startswith("#"):
            filters[line.split()[0]] = float(line.split()[1])

    # make a file to write results to
    # results = open("/Users/gbbtz7/GoogleDrive/Research/Data/equivalent_redshifts.txt", "w")
    # results.write("# Equivalent redshifts for given filter combinations. Check equivalent_redshifts.py for details.\n"
    #        "#\n")

    filter_pairs = [("r","z"), ("f814w", "f140w")]   #These are the filter pairs that will be used to calculate redshifts

    for filter_pair in filter_pairs:
        print(filter_pair)  # for debugging

        shorter_filter_wavelength = filters[filter_pair[0]]
        longer_filter_wavelength = filters[filter_pair[1]]

        # find the redshift where the filter sees U-V
        first_UV_z = equivalent_redshift(filters["U"], shorter_filter_wavelength)
        second_UV_z = equivalent_redshift(filters["V"], longer_filter_wavelength)
        # since these redshifts won't be completely identical, average them to get an equivalent redshift
        U_z = (first_UV_z + second_UV_z) / 2
        print first_UV_z, second_UV_z, U_z

        #find where filter pair sees B-R
        first_BR_z = equivalent_redshift(filters["B"], shorter_filter_wavelength)
        second_BR_z = equivalent_redshift(filters["R"], longer_filter_wavelength)
        # since these redshifts won't be completely identical, average them to get an equivalent redshift
        U_z = (first_BR_z + second_BR_z) / 2
        print first_BR_z, second_BR_z, U_z

        # find the redshift where the filter sees V-I
        first_VI_z = equivalent_redshift(filters["V"], shorter_filter_wavelength)
        second_VI_z = equivalent_redshift(filters["I"], longer_filter_wavelength)
        # since these redshifts won't be completely identical, average them to get an equivalent redshift
        U_z = (first_VI_z + second_VI_z) / 2
        print first_VI_z, second_VI_z, U_z
        # Save these results to a file for easy use later


print os.path.dirname(os.path.realpath(__file__))

make_all_equiv_z()

