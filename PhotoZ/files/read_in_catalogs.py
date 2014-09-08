from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import catalog
from PhotoZ.files import Cluster
from PhotoZ.files import other_classes
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
            this_cluster = Cluster.Cluster(cluster_name, [])
            cluster_list.append(this_cluster)



        # Use regular expressions to determine what type a catalog is.
        sextractor_catalog = re.compile(r"MOO[0-9]{4}([+]|[-])[0-9]{4}_(r|z)[.]cat")
        # MOO, 4 digits, + or -, 4 more digits, _, r or z, .cat

        gemini_catalog = re.compile(r"m[0-9]{4}(p|m)[0-9]{4}[.]phot[.]dat")
        # m, 4 digits, p or m, 4 more digits, .phot.dat

        irac_catalog = re.compile(r"MOO_[0-9]{4}([+]|[-])[0-9]{4}_irac1_bg[.]fits[.]cat")
        # MOO_, 4 digits, + or -, 4 more digits, _irac_bg.fits.cat

        if sextractor_catalog.match(cat_filename):  # If it is a SExtractor catalog
            # find the band the catalog has data for
            band = functions.get_band_from_filename(cat_filename)

            # Read in the catalog
            cat_table = catalog.read_catalog(cat, ["ALPHA_J2000", "DELTA_J2000", "MAG_APER", "MAGERR_APER"],
                                             label_type="m", data_start=8, filters=["FLAGS < 4"])
            # Turn the table into source objects, and assign source list to cluster object
            this_cluster.sources_list = [other_classes.Source(line[0], line[1], [band], [line[2]], [line[3]])
                                         for line in cat_table]


        elif gemini_catalog.match(cat_filename):  # catalogs that end in .phot.dat
            # Have less desirable formatting, so need to be wrangled
            # Read in the catalog data
            cat_table = catalog.read_catalog(cat, ["ra", "dec", 3, 4, 5], label_type='s', label_row=0, data_start=2)
            # Columns 3, 4, 5 are mag, color, color error

            # find the bands in the catalog
            band_labels = catalog.column_labels(cat, [3, 4])
            if band_labels[1] == 'rmz':
                band = 'r'
            elif band_labels[1] == 'imch1':
                band = 'i'
            elif band_labels[1] == 'ch1mch2':
                band = 'ch1'

            # Convert them to source objects
            this_cluster.sources_list = [other_classes.Source(line[0], line[1], mag_bands=[band], mags=[line[2]],
                                                              mag_errors=[0], color_bands=[band_labels[1]],
                                                              color_values=[line[3]], color_errors=[line[4]])
                                         for line in cat_table]



        elif irac_catalog.match(cat_filename):
            pass # Don't do anything with them for now.

        else:
            print cat_filename, "no match"

    return cluster_list

