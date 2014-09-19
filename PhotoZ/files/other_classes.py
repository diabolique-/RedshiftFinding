import math

class Source(object):
    """Class representing a source detected by SExtractor. Holds data in all bands that exist for the object."""

    def __init__(self, ra, dec, mag_bands, mags, mag_errors, color_bands=None, color_values=None, color_errors = None):
        """Create a galaxy object using the information passed in."""
        self.ra = float(ra)
        self.dec = float(dec)
        self.mags = dict()
        self.mag_residuals = dict()
        self.colors = dict()
        if len(mag_bands) == len(mags) == len(mag_errors):
            for i in range(len(mag_bands)):
                self.mags[mag_bands[i]] = data(mags[i], mag_errors[i])

        # In only need this part because of the dumb color catalogs. SExtractor input is so much easier.
        if color_bands and color_values and color_errors:
            if len(color_bands) == len(color_values) == len(color_errors):
                # first make color bands have minuses instead of ms
                fixed_color_bands = [c.replace("m", "-") for c in color_bands]
                for i in range(len(fixed_color_bands)):
                    self.colors[fixed_color_bands[i]] = data(color_values[i], color_errors[i])

        # Assume it is not a RS member for now, this will change as the code runs.
        self.RS_member = False

    def add_band_data(self, mag_band, mag, mag_error):
        self.mags[mag_band] = data(mag, mag_error)

    def init_color(self, mag_band, mag, color_bands, color, color_error):
        self.mags = dict

    def __repr__(self):  # Shows how sources are printed.
        return "(" + "ra=" + str(self.ra) + ", dec=" + str(self.dec) + ")"

    def find_mag_residual(self, band, comparison_mag):
        """Calculate the magnitude residual, compared to some known magnitude.
        :param band: band the data is in
        :param comparison_mag: known magnitude to be compared.
        :return: none, but the instance attribute for the source's mag_residual attribute is set.
        """
        self.mag_residuals[band] = data(comparison_mag - self.mags[band].value, self.mags[band].error)

    def calculate_color(self):
        print self.mags
        for band1 in self.mags:
            for band2 in self.mags:
                if not band1 == band2:
                    self.colors[band1 + "-" + band2] = self.mags[band1] - self.mags[band2]
                    # That line does the error things automatically, since noth mags are data objects
        print self.colors


class data(object):
    """Class that represents a data point. Has a value and a error attribute."""
    def __init__(self, value, error):
        self.value = value
        self.error = error
    def __repr__(self):
        return str(self.value) + "+-" + str(self.error)
    # TODO: get an actual plus minus sign in there
    def __add__(self, other):
        """ Redefines the addition operator to return a data object. Adds values, and adds errors in quadrature.

        :param other: has to be a data object
        :return: data object with the correct thing
        """
        return data(self.value + other.value, math.sqrt((self.error)**2 + (other.error)**2))

    def __sub__(self, other):
        """Redefines the subtraction operator to return a data object. Ads values, and adds errors in quadrature.
        :param other: has to be another data object
        :return: data object
        """
        return data(self.value - other.value, math.sqrt(self.error**2 + other.error**2))


class EndProgramError(Exception):
    """Exception class that ends the program when raised. Prints an error message,
    as well as optionally printing a value that caused the exception.
    """
    def __init__(self, message, offending_value=None):
        print message
        if offending_value:
            print "Here is the offending value: " + str(offending_value)
        raise Exception  # Exits the program