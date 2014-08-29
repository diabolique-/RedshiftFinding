class Source(object):
    """Class representing a source detected by SExtractor. Holds data in all bands that exist for the object."""

    def __init__(self, ra, dec, bands, mags, mag_errors):
        """Create a galaxy object using the information passed in."""
        self.ra = float(ra)
        self.dec = float(dec)
        self.mags = dict()
        self.mag_errors = dict()
        self.mag_residuals = dict()
        self.color_residuals = dict()
        if len(bands) == len(mags) == len(mag_errors):
            for i in range(len(bands)):
                self.mags[bands[i]] = data(mags[i], mag_errors[i])


        # Assume it is not a RS member for now, this will change as the code runs.
        self.RS_member = False

    def __repr__(self):  # Shows how sources are printed.
        return str("ra=" + str(self.ra) + ", dec=" + str(self.dec))

    def find_mag_residual(self, band, comparison_mag):
        self.mag_residuals[band] = data(comparison_mag - self.mags[band].value, self.mags[band].error)

# TODO: add calculations of color


class data(object):
    def __init__(self, value, error):
        self.value = value
        self.error = error
    def __repr__(self):
        return str(self.value) + "+-" + str(self.error)
    # TODO: get an actual plus minus sign in there
