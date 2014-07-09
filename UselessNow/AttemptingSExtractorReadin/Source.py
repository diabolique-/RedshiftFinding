class Source(object):
    """
    Class for storing objects read on from a SExtractor catalog. Stores all the info provided by tha catalog.
    May also calculate some things
    """
    def __init__(self, data_list, default_param_filename):
        """Initialize the galaxy object, taking in all the information from the SExtractor catalog.
        Data will be stored in a dictionary, using the names from the SExtractor default params"""

        # open the default parameters list
        params = open(default_param_filename, 'r')

        # create the dictionary the data will be stored in
        data = dict()

        # make a list of the parameters that are output by the SExtractor run
        params_list = []

        # iterate through the param f, and either add to dictionary as not available, or add to list
        for line in params:
            if line.startswith('#'):
                # add parameter to dictionary with value of "not available"
                data[line[1:]] = "not available"
            # need to handle parameters with multiple appearances (like if we used 2 apertures)
            elif line.endswith(")"):  # SExtractor always indicates this with (# of appearances)
                # START HERE NEXT!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            elif len(line) > 2:
                params_list.append(line.strip())  #remove whitespaces

        print params_list

        #print data

        # print data_list
        # Continue with the rest of the attributes, not sure what they are at this point

    def __repr__(self):
        """Return something to represent this object NEEDS TO BE FLESHED OUT, OBVIOUSLY"""
        return "hello"