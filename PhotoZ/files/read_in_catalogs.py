from PhotoZ.files import functions
from PhotoZ.files import global_paths
from PhotoZ.files import catalog

def read_sex_catalogs():
    # TODO: document

    # First find all catalogs
    catalog_path_list = functions.find_all_objects(global_paths.catalogs_look_directory, [".cat", ".dat"], [])

    # Initialize an empty list of clusters
    cluster_list = []

    for cat in catalog_path_list:
        # Match the catalog to a cluster if there is one already in the list with the same name. If not,
        # make a new cluster with that name.
        print functions.make_cluster_name(cat.split("/")[-1])

        # Use regular expressions to determine what type a catalog is.
        if cat.endswith(".cat"): # Will be a SExtractor catalog
            # Read in the catalog
            cat_table = catalog.read_catalog(cat, ["ALPHA_J2000", "DELTA_J2000", "MAG_APER", "MAGERR_APER"],
                                             label_type="m", data_start=8, filters=["FLAGS < 4"])

