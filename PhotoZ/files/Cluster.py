class Cluster(object):
    """

    """
    # tODO: document

    def __init__(self, name, sources_list, spec_z=None):
        # TODO: document
        # Assign the cluster's name, and the spectroscopic redshift, if it exists.
        self.name = name
        if spec_z:
            self.spec_z = spec_z
        else:
            self.spec_z = None

        self.sources_list = sources_list

    def __repr__(self):  # how the object appears when printed
        return self.name + "; spec z = " + str(self.spec_z)
