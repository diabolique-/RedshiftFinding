import urllib
import os.path
from PhotoZ.files import catalog
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import other_classes
import matplotlib.pyplot as plt
import numpy as np

def sdss_calibration(sex_sources, sdss_sources, band):



    # Now need to match stars in sex_sources to those in SDSS
    pairs = []
    for source in sex_sources:
        match = match_sources(source, sdss_sources)
        if match:
            pairs.append((source, match))
    if len(pairs) == 0:  # If matching didn't work
        return False


    # Now we have pairs of matching objects. We can now calculate the magnitude differences for each one.
    # Difference = SDSS mag - measured mag
    for pair in pairs:
        pair[0].find_mag_residual(band, pair[1].mags[band].value)

    # a good first guess is an average of all differences
    mag_differences = [pair[0].mag_residuals[band].value for pair in pairs]
    first_guess = sum(mag_differences)/len(mag_differences)

    # throw out outliers
    pairs = [pair for pair in pairs if abs(pair[0].mag_residuals[band].value - first_guess) < 0.3]

    # now fit a chi_squared
    best_chi_squared = 99999999999999999999999
    best_intercept = 9999999
    for i in np.arange(first_guess-0.5, first_guess+0.5, 0.01):
        chi_squared = 0.0
        for pair in pairs:
            # print pair[0].mag_residuals[band]
            chi_squared += ((pair[0].mag_residuals[band].value - i)/pair[0].mag_residuals[band].error)**2
        if chi_squared < best_chi_squared:
            best_chi_squared = chi_squared
            best_intercept = i



    return best_intercept




def match_sources(source, source_list):

    pairs = []  # initialize empty list, will append as we go

    closest_dist = 999
    closest_source = None
    for source_2 in source_list:
        dist = functions.distance(source.ra, source_2.ra, source.dec, source_2.dec)
        if dist < closest_dist:
            closest_dist = dist
            closest_source = source_2
    # I'll accept them as pairs if the distance is less than an arcsecond between them. That is enough error
    if closest_dist < 1.0/3600.0:
        return closest_source
    else:
        return None


def _call_sdss_sql(command, format="csv"):

    url = 'http://cas.sdss.org/public/en/tools/search/x_sql.asp?'

    params = urllib.urlencode({'cmd': command, 'format': format})
    my_file = urllib.urlopen(url + params)
    return my_file.readlines()

def make_sdss_catalog(stars_catalog, path):

    # TODO: document

    #If there aren't any star objects in the catalog, then calibrating to SDSS won't work.
    if len(stars_catalog) < 1:
        return False

    # find coordinate limits, to restrict locations of the SDSS query. Leave some margin for error, too
    min_ra = min([star[2] for star in stars_catalog]) - 0.001
    min_dec = min([star[3] for star in stars_catalog]) - 0.001
    max_ra = max([star[2] for star in stars_catalog]) + 0.001
    max_dec = max([star[3] for star in stars_catalog]) + 0.001



    # Create command using templates. Basically, the things at the end replace the %s each time. The s indicates string.
    command = "select ra,dec,u,g,r,i,z from PhotoObj where ra between %s and %s and dec between %s and %s " \
              "and (u between 17.0 and 20.5 or g between 17.0 and 20.5 or r between 17.0 and 20.5 or i between 17.0 " \
              "and 20.5 or z between 17.0 and 20.5)" %(min_ra, max_ra, min_dec, max_dec)
    # and r between 17.0 and 20.5 or z between 17.0 and 20.5
    # That mag cut didn't work when I tried implementing it for some reason
    lines = _call_sdss_sql(command)
    lines = [line.strip().split(",") for line in lines]

    # Check that there are actually objects returned.
    if lines[0][0].startswith("No objects"):
        return False

    # Now have list of lists that is like a table
    # Now need to write it to the file
    #

    catalog = open(path, "w")
    lines = [" ".join(line) for line in lines]  # join each element into one string, separated by spaces
    total_file = "\n".join(lines)  # join lines into one big file, separated with newlines
    catalog.write(total_file)
    catalog.close()

    return True


# def fit_zero_slope_line(points, intercepts):
#     best_intercept = 999
#     best_chi_square_value = 999999
#     for i in intercepts:
#         chi_square = 0
#         for point in points:

