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

        self.r_data = False
        self.i_data = False
        self.z_data = False
        self.ch1_data = False
        self.ch2_data = False

    def __repr__(self):  # how the object appears when printed
        return self.name

    def calculate_color(self):
        for source in self.sources_list:
            source.calculate_color()
