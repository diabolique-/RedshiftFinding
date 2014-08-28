class Source(object):
    """Class representing a source detected by SExtractor. Holds data in all bands that exist for the object."""

    def __init__(self, ra, dec, bands, mags, mag_errors=None):
        """Create a galaxy object using the information passed in."""
        self.ra = float(ra)
        self.dec = float(dec)
        self.mags = dict()
        if len(bands) == len(mags):
            for i in range(len(bands)):
                self.mags[bands[i]] = mags[i]
                    # Only used in calibration, where I know the bands are the same, and I don't want to mess with
                    # finding the band, and converting that to a variable call
                # TODO: should just use a dictionary for mags.
                # TODO: add IR bands

        # TODO: add errors

        # Assume it is not a RS member for now, this will change as the code runs.
        self.RS_member = False

    def __repr__(self):  # Shows how sources are printed.
        return str("ra=" + str(self.ra) + ", dec=" + str(self.dec))

# TODO: add calculations of color