class Source(object):
    """Class representing a source detected by SExtractor. Holds data in all bands that exist for the object."""

    def __init__(self, id_num, ra, dec, r_mag=None, z_mag=None, ch1_mag=None, ch2_mag=None):
        """Create a galaxy object using the information passed in."""
        self.id = int(id_num)  # TODO: do I really need ID? What purpose does it serve?
        self.ra = float(ra)
        self.dec = float(dec)
        self.r_mag = r_mag
        self.z_mag = z_mag
        self.ch1_mag = ch1_mag
        self.ch2_mag = ch2_mag

        # Can calculate colors from this data
        if self.r_mag and self.z_mag:
            self.rz_color = self.r_mag - self.z_mag
        # TODO: add other color combinations

        # Assume it is not a RS member for now, this will change as the code runs.
        self.RS_member = False

    def __repr__(self):  # Shows how sources are printed.
        return str(str(self.id) + ", ra=" + str(self.ra) + ", dec=" + str(self.dec))