import Source


class Image(object):
    """Class that holds the information for a single image. Has a list of all the galaxies in it"""

    def __init__(self, sex_catalog_filename):
        """Initialize the image object"""

        # Start with an empty list of sources, that will be populated later
        self.source_list = []

        # Open the f for reading
        catalog = open(sex_catalog_filename, 'r')

        # Need to initialize an empty list for data, so I can append to it
        data = []

        # Then start reading it in
        for line in catalog:
            if not line.startswith("#"):  # Ignore comments at the top
                # Split the line into individual data elements before appending
                data.append(line.split())

        # Now want to make galaxy objects out of this data
        # Need to iterate through each line, which represents a galaxy
        for line in range(len(data)):
            # Create a source object for the data in the line, and append this object to the list of sources
            self.source_list.append(Source.Source(data[line], "test.param"))

    # How do I define the red sequence?