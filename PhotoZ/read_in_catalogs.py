from PhotoZ import functions
from PhotoZ import global_paths
from PhotoZ import catalog
from PhotoZ import Cluster
from PhotoZ import other_classes
from PhotoZ import sdss_calibration
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
            # make one
            this_cluster = Cluster.Cluster(cluster_name, [])
            cluster_list.append(this_cluster)

        # Use regular expressions to determine what type a catalog is.
        sextractor_catalog = re.compile(r"MOO[0-9]{4}([+]|[-])[0-9]{4}_sloan_(r|z)[.]cat")
        # MOO, 4 digits, + or -, 4 more digits, _, r or z, .cat

        gemini_catalog = re.compile(r"m[0-9]{4}(p|m)[0-9]{4}[.]phot[.]dat")
        # m, 4 digits, p or m, 4 more digits, .phot.dat

        irac_catalog = re.compile(r"MOO_[0-9]{4}([+]|[-])[0-9]{4}_irac1_bg[.]fits[.]cat")
        # MOO_, 4 digits, + or -, 4 more digits, _irac_bg.fits.cat

        keck_catalog = re.compile(r"m[0-9]{4}(p|m)[0-9]{4}[.]zr[.]cat")

        if sextractor_catalog.match(cat_filename):  # If it is a SExtractor catalog
            # find the band the catalog has data for
            band = cat_filename[13:-4]

            # tell the cluster it has data in this band
            this_cluster.bands.add(band)

            # Read in the catalog
            cat_table = catalog.read_catalog(cat, ["ALPHA_J2000", "DELTA_J2000", "MAG_APER", "MAGERR_APER", "NUMBER"],
                                             label_type="m", data_start=8, filters=["FLAGS < 4"])

            # Match sources to existing ones in the cluster
            for line in cat_table:
                # Create a source object based on the band
                if band == "sloan_r":
                    this_source = other_classes.Source(line[0], line[1], [band], [line[2]], [line[3]], r_id=line[4])
                elif band == "sloan_z":
                    this_source = other_classes.Source(line[0], line[1], [band], [line[2]], [line[3]], z_id=line[4])

                # see if an object with a matching IS number already exists in the cluster sources_list
                for source in this_cluster.sources_list:
                    if source.r_id == line[4] or source.z_id == line[4]:   # line[4] holds id numbers
                        matching_source = source
                        break
                else:  # No break, didn't find an match based on ID. Will match on ra/dec
                    matching_source = sdss_calibration.find_match(this_source, this_cluster.sources_list)
                # Will return either a source object or None
                if matching_source:  # If it already exists in the cluster
                    matching_source.add_band_data(band, line[2], line[3])
                else:  # If it doesn't exist, append it
                    this_cluster.sources_list.append(this_source)



        elif gemini_catalog.match(cat_filename):  # catalogs that end in .phot.dat
            # Read in the catalog data
            cat_table = catalog.read_catalog(cat, ["ra", "dec", 3, 4, 5], label_type='s', label_row=0, data_start=2)
            # Columns 3, 4, 5 are mag, color, color error

            # find the bands in the catalog, and let the cluster know it has data in these bands
            band_labels = catalog.get_column_labels(cat, [3, 4])
            if band_labels[1] == 'rmz':
                band = 'sloan_z'
                color = "sloan_r-sloan_z"
                this_cluster.bands.add("sloan_z")
                this_cluster.bands.add("sloan_r")
            elif band_labels[1] == 'imch1':
                band = 'ch1'
                color = "sloan_i-ch1"
                this_cluster.bands.add("sloan_i")
                this_cluster.bands.add("ch1")
            elif band_labels[1] == 'ch1mch2':
                band = 'ch2'
                color = "ch1-ch2"
                this_cluster.bands.add("ch1")
                this_cluster.bands.add("ch2")

            # Convert them to source objects
            # I don't worry about adding each source at once, since clusters that are from these catalogs will not be
            #  used with any other catalogs. They are independent.
            this_cluster.sources_list = [other_classes.Source(line[0], line[1], mag_bands=[band], mags=[line[2]],
                                                              mag_errors=[0], color_bands=[color],
                                                              color_values=[line[3]], color_errors=[line[4]])
                                         for line in cat_table]

        elif keck_catalog.match(cat_filename):
            # read in catalog
            cat_table = catalog.read_catalog(cat, ["x", "y", "zmag", "zerr", "rmag", "rerr"],
                                             label_type="s",
                                             label_row=0, data_start=1, filters=["zflag < 4", "rflag < 4"])

            # let the cluster know it has data in r and z
            this_cluster.bands.add("sloan_r")
            this_cluster.bands.add("sloan_z")

            # convert to source objects
            this_cluster.sources_list = [other_classes.Source(line[0], line[1], ["r", "z"], mags=[line[4], line[2]],
                                                              mag_errors=[
                line[5], line[3]]) for line in cat_table]




        elif irac_catalog.match(cat_filename):
            pass
            # cat_table = catalog.read_catalog(cat, [1, 2, 3, 4, 5], label_type="s", label_row=0, data_start=1)
            # # columns are ra, dec, ch1 flux [uJy], ch2 flux[uJy], ch1-ch2 color(Vega)
            #
            # # # need to convert the fluxes to AB magnitudes
            # # for line in cat_table:
            # #     if type(line[2]) != float or type(line[3]) != float:
            # #         print cat_filename
            # #         print line
            #
            # mags_table =[[line[0], line[1], functions.uJansky_to_AB_mag(line[2]),
            #               functions.uJansky_to_AB_mag(line[3]), line[4]] for line in cat_table]
            # # TODO: colors are still in Vega!!!
            # print mags_table


        else:
            print cat_filename, "no match"

    return cluster_list

