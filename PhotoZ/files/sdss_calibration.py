import urllib
import os.path
from PhotoZ.files import catalog
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import other_classes
import matplotlib.pyplot as plt
import numpy as np

def sdss_calibration(sex_catalog_path):

    # read the SExtractor catalog with my read_catalog_function. Pick out stars of a given mag range
    sex_stars = catalog.read_catalog(sex_catalog_path,
                                     desired_columns=["MAG_APER", "MAGERR_APER", "ALPHA_J2000", "DELTA_J2000"],
                                     label_type="m", label_row=0, data_start=8,
                                     filters=["FLAGS < 4", "MAGERR_APER < 0.2", "CLASS_STAR > 0.8", "MAG_APER > 17",
                                              "MAG_APER < ""20.5"])
    # TODO: ask Brodwin about how good this is. Is CLASS_STAR > 0.8 too constricting, or not constricting enough?

    #If there aren't any star objects in the catalog, then calibrating to SDSS won't work.
    if len(sex_stars) < 1:
        return False

    # find coordinate limits, to restrict locations of the SDSS query. Leave some margin for error, too
    min_ra = min([star[2] for star in sex_stars]) - 0.001
    min_dec = min([star[3] for star in sex_stars]) - 0.001
    max_ra = max([star[2] for star in sex_stars]) + 0.001
    max_dec = max([star[3] for star in sex_stars]) + 0.001

    # find the name of the SDSS catalog. catalogs path + name (derived from Sextractor catalog) + band_sdss.cat
    sdss_catalog_path = global_paths.calibration_catalogs_directory + sex_catalog_path.split("/")[-1].split("_")[0] + \
                                                                     "_sdss.cat"
    # See if the catalog exists, and if it doesn't, make it
    if not os.path.isfile(sdss_catalog_path):
        has_objects = make_sdss_catalog(min_ra, max_ra, min_dec, max_dec, sdss_catalog_path)
        # Check to see if there are actually objects in the catalog. If not, exit, since calibration won't work.
        if has_objects is False:
            return False

    # find the band of the SExtractor catalog, so we know what to calibrate
    band = functions.get_band_from_filename(sex_catalog_path.split("/")[-1])

    # Read the sdss catalog
    sdss_catalog = catalog.read_catalog(sdss_catalog_path, ["ra", "dec", band], label_type="s", label_row=0)

    # Each line is a source, so turn it into that.
    sdss_sources = [other_classes.Source(line[0], line[1], bands=[band], mags=[line[2]], mag_errors=[0])
                    for line in sdss_catalog]
    sex_sources = [other_classes.Source(line[2], line[3], bands=[band], mags=[line[0]], mag_errors=[line[1]])
                   for line in sex_stars]

    # Now need to match stars in sex_sources to those in SDSS
    pairs = []  # initialize empty list, will append as we go
    for star in sex_sources:
        closest_dist = 999
        closest_sdss_obj = None
        for sdss_obj in sdss_sources:
            dist = functions.distance(star.ra, sdss_obj.ra, star.dec, sdss_obj.dec)
            if dist < closest_dist:
                closest_dist = dist
                closest_sdss_obj = sdss_obj
        # I'll accept them as pairs if the distance is less than an arcsecond between them. That is enough error
        if closest_dist < 1.0/3600.0:
            pairs.append((star, closest_sdss_obj))

    # Now we have pairs of matching objects. We can now calculate the magnitude differences for each one.
    # Difference = SDSS mag - measured mag
    for pair in pairs:
        pair[0].find_mag_residual(band, pair[1].mags[band].value)

    # a good first guess is an average of all differences
    mag_differences = [pair[0].mag_residuals[band].value for pair in pairs]
    first_guess = sum(mag_differences)/len(mag_differences)

    # throw out outliers
    pairs = [pair for pair in pairs if abs(pair[0].mag_residuals[band].value - first_guess) < 0.05]
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

    user_approved = False
    while not user_approved:
        sdss_mags, mag_differences, mag_errors = [], [], []
        for pair in pairs:
            sdss_mags.append(pair[1].mags[band].value)
            mag_differences.append(pair[0].mag_residuals[band].value)
            mag_errors.append(pair[0].mags[band].error)
        plt.errorbar(sdss_mags, mag_differences, mag_errors, fmt=".", c="k")
        plt.axhline(best_intercept, c="r")
        plt.axhline(first_guess, c="k")
        plt.show()
        user_input = raw_input("Does this look good? (y/n) ")
        print user_input
        if user_input == "Y" or "y":
            user_approved = True
        else:
            user_approved = False

    # Don't need to fit a line. Since the x values don't matter (since the slope is zero), I can just do a weighted
    # average thing (based on errorbars) of the mag differences to find the best fit.


    return True  # It worked properly







def _call_sdss_sql(command, format="csv"):

    url = 'http://cas.sdss.org/public/en/tools/search/x_sql.asp?'

    params = urllib.urlencode({'cmd': command, 'format': format})
    my_file = urllib.urlopen(url + params)
    return my_file.readlines()

def make_sdss_catalog(min_ra, max_ra, min_dec, max_dec, path):

    # TODO: document

    # Create command using templates. Basically, the things at the end replace the %s each time. The s indicates string.
    command = "select ra,dec,u,g,r,i,z from PhotoObj where ra between %s and %s and dec between %s and %s and type=6 " \
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

