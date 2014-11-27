from PhotoZ.files import Cluster
from PhotoZ.files import functions

def _determine_which_cluster(clusters_list, catalog_name):
    # TODO: document
    name = functions.make_cluster_name(catalog_name)

    for c in clusters_list:
        if c.name == name:
            return c

    # Since we got this far, we know it's not in the list. We now initialize a new cluster object with empty
    clusters_list.append(Cluster.Cluster(name, []))
    return clusters_list[-1]

