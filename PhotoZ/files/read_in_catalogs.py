from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import catalog
import re

def read_sex_catalogs():
    # TODO: document

    # First find all catalogs
    catalog_path_list = functions.find_all_objects(global_paths.catalogs_look_directory, [".cat", ".dat"], [])

    # Initialize an empty list of clusters
    cluster_list = []

    for cat in catalog_path_list:
        # Match the catalog to a cluster if there is one already in the list with the same name. If not,
        # make a new cluster with that name.
        cat_filename = cat.split("/")[-1]
        cluster_name = functions.make_cluster_name(cat_filename)

        for c in cluster_list:
            if c.name == cluster_name:
                this_cluster = c
                break
        else: # no break, which means a matching cluster wasn't found
            pass
            #this_cluster = # TODO: need to write the cluster class. ASsign this to a new cluster class object


        # Use regular expressions to determine what type a catalog is.
        sextractor_catalog = re.compile(r"MOO[0-9]{4}([+]|[-])[0-9]{4}_(r|z)[.]cat")
        # MOO, 4 digits, + or -, 4 more digits, _, r or z, .cat

        gemini_catalog = re.compile(r"m[0-9]{4}(p|m)[0-9]{4}[.]phot[.]dat")
        # m, 4 digits, p or m, 4 more digits, .phot.dat

        irac_catalog = re.compile(r"MOO_[0-9]{4}([+]|[-])[0-9]{4}_irac1_bg[.]fits[.]cat")
        # MOO_, 4 digits, + or -, 4 more digits, _irac_bg.fits.cat

        if sextractor_catalog.match(cat_filename):
            print cluster_name, "sex"
        elif gemini_catalog.match(cat_filename):
            print cluster_name, 'gemini'
        elif irac_catalog.match(cat_filename):
            print cluster_name, "irac"

        else:
            print cat_filename, "no match"


        # if cat.endswith(".cat"): # Will be a SExtractor catalog
        #     # Read in the catalog
        #     cat_table = catalog.read_catalog(cat, ["ALPHA_J2000", "DELTA_J2000", "MAG_APER", "MAGERR_APER"],
        #                                      label_type="m", data_start=8, filters=["FLAGS < 4"])

