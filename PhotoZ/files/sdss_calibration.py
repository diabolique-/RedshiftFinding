import urllib
import os.path
from PhotoZ.files import catalog
from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import other_classes
import matplotlib.pyplot as plt

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
        return

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
        make_sdss_catalog(min_ra, max_ra, min_dec, max_dec, sdss_catalog_path)

    # find the band of the SExtractor catalog, so we know what to calibrate
    band = functions.get_band_from_filename(sex_catalog_path.split("/")[-1])

    # Read the sdss catalog
    sdss_catalog = catalog.read_catalog(sdss_catalog_path, ["ra", "dec", band], label_type="s", label_row=0)

    # Each line is a source, so turn it into that.
    # NOTE: since both the SDSS and SExtractor sources are in the same band, I can use the generic_mag
    sdss_sources = [other_classes.Source(line[0], line[1], bands=[band], mags=[line[2]]) for line in sdss_catalog]
    sex_sources = [other_classes.Source(line[2], line[3], bands=[band], mags=[line[0]]) for line in sex_stars]

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
    mag_differences = []
    sdss_mags = []
    for pair in pairs:
        sdss_mags.append(pair[1].mags[band])
        mag_differences.append(pair[1].mags[band] - pair[0].mags[band])

    plt.scatter(sdss_mags, mag_differences)
    plt.show()









def _call_sdss_sql(command, format="csv"):

    url = 'http://cas.sdss.org/public/en/tools/search/x_sql.asp?'

    params = urllib.urlencode({'cmd': command, 'format': format})  # fsql is command string
    my_file = urllib.urlopen(url + params)
    return my_file.readlines()

def make_sdss_catalog(min_ra, max_ra, min_dec, max_dec, path):
    # TODO: see how bands are handled in the rest of my code to see the best way
    # to handle band information here. Probably be better with a list of bands
    # that need to be wrangled into the right form. This inplementation is
    # the simplest and stupidest way to do it.

    # TODO: document

    # Create command using templates. Basically, the things at the end replace the %s each time. The s indicates string.
    command = "select ra,dec,u,g,r,i,z from PhotoObj where ra between %s and %s and dec between %s and %s and type=6 " \
              "and (u between 17.0 and 20.5 or g between 17.0 and 20.5 or r between 17.0 and 20.5 or i between 17.0 " \
              "and 20.5 or z between 17.0 and 20.5)" %(min_ra, max_ra, min_dec, max_dec)
    # and r between 17.0 and 20.5 or z between 17.0 and 20.5
    # That mag cut didn't work when I tried implementing it for some reason
    lines = _call_sdss_sql(command)
    lines = [line.strip().split(",") for line in lines]

    # Now have list of lists that is like a table
    # Now need to write it to the file

    # TODO: check for errors from SDSS. File will start with ERROR
    # TODO: make this integrate with my actual file structure
    catalog = open(path, "w")
    lines = [" ".join(line) for line in lines]  # join each element into one string, separated by spaces
    total_file = "\n".join(lines)  # join lines into one big file, separated with newlines
    catalog.write(total_file)
    catalog.close()



