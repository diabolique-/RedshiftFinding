import urllib
from PhotoZ.files import catalog
from PhotoZ.files import functions
from PhotoZ.files import global_paths

def sdss_calibration(sex_catalog_path):

    # read the SExtractor catalog with my read_catalog_function
    sex_stars = catalog.read_catalog(sex_catalog_path,
                                     desired_columns=["MAG_APER", "MAGERR_APER", "ALPHA_J2000", "DELTA_J2000"],
                                     label_type="m", label_row=0, data_start=8,
                                     filters=["FLAGS < 4", "MAGERR_APER < 0.2", "CLASS_STAR > 0.9", "MAG_APER > 17",
                                              "MAG_APER < ""20.5"])
    # first find the band of the catalog
    band = functions.get_band_from_filename(sex_catalog_path.split("/")[-1])
    # find coordinate limits, to restrict locations of the SDSS query
    min_ra = min([star[2] for star in sex_stars])
    min_dec = min([star[3] for star in sex_stars])
    max_ra = max([star[2] for star in sex_stars])
    max_dec = max([star[3] for star in sex_stars])

    # create catalog of SDSS stars in the region
    make_sdss_catalog(min_ra, max_ra, min_dec, max_dec, band)


def _call_sdss_sql(command, format="csv"):

    url = 'http://cas.sdss.org/public/en/tools/search/x_sql.asp?'

    params = urllib.urlencode({'cmd': command, 'format': format})  # fsql is command string
    my_file = urllib.urlopen(url + params)
    return my_file.readlines()

def make_sdss_catalog(min_ra, max_ra, min_dec, max_dec, bands):
    # TODO: see how bands are handled in the rest of my code to see the best way
    # to handle band information here. Probably be better with a list of bands
    # that need to be wrangled into the right form. This inplementation is
    # the simplest and stupidest way to do it.

    # TODO: document

    # Create command using templates. Basically, the things at the end replace the %s each time. The s indicates string.
    command = "select ra,dec,%s from PhotoObj where ra between %s and %s and dec between %s and %s and type=6" \
              %(bands, min_ra, max_ra, min_dec, max_dec)
    # and r between 17.0 and 20.5 or z between 17.0 and 20.5
    # That mag cut didn't work when I tried implementing it for some reason
    lines = _call_sdss_sql(command)
    lines = [line.strip().split(",") for line in lines]

    # Now have list of lists that is like a table
    # Now need to write it to the file

    # TODO: check for errors from SDSS. File will start with ERROR
    # TODO: make this integrate with my actual file structure
    catalog = open("/Users/gbbtz7/Desktop/sdss.cat", "w")
    for line in lines:
        for thing in line:
            catalog.write(thing + " ")
        catalog.write("\n")

    catalog.close()



