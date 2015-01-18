# coding=utf-8


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


# Read in the effective wavelengths of the filters
filter_data = open("/Users/gbbtz7/GoogleDrive/Research/Data/Eisenhardt2007filters_effective.dat", "r")

# make a dictionary that holds the filter name, and its effective wavelength
filters = {line.split()[0]: float(line.split()[1]) for line in filter_data}

# Find the redshift where r-z sees U-V
redshift_U_r = equivalent_redshift(filters["U"], filters["Sloan_r"])
redshift_V_z = equivalent_redshift(filters["V"], filters["Sloan_z"])
# Since these redshifts aren't exactly the same, average them to get an equivalent redshift for the given color
redshift_UV_rz = (redshift_U_r + redshift_V_z ) / 2

# Find the redshift where r-z sees B-R
redshift_B_r = equivalent_redshift(filters["B"], filters["Sloan_r"])
redshift_R_z = equivalent_redshift(filters["R"], filters["Sloan_z"])
# Since these redshifts aren't exactly the same, average them to get an equivalent redshift for the given color
redshift_BR_rz = (redshift_B_r + redshift_R_z ) / 2

# Find the redshift where r-z sees V-I
redshift_V_r = equivalent_redshift(filters["V"], filters["Sloan_r"])
redshift_I_z = equivalent_redshift(filters["I"], filters["Sloan_z"])
# Since these redshifts aren't exactly the same, average them to get an equivalent redshift for the given color
redshift_VI_rz = (redshift_V_r + redshift_I_z ) / 2

# Save these results to a file for easy use later
file = open("/Users/gbbtz7/GoogleDrive/Research/Data/equivalent_redshifts.dat", "w")
file.write("# Equivalent redshifts for given filter combinations. Check equivalent_redshifts.py for details.\n"
           "#\n"
           "# r-z to U-V\n" +
           str(redshift_UV_rz) + "\n" +
           "# r-z to B-R\n" +
           str(redshift_BR_rz) + "\n" +
           "# r-z to V-I\n" +
           str(redshift_VI_rz))

