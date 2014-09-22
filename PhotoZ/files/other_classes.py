import math
import numpy as np

# TODO: document

class Source(object):
    """Class representing a source detected by SExtractor. Holds data in all bands that exist for the object."""

    def __init__(self, ra, dec, mag_bands, mags, mag_errors, color_bands=None, color_values=None, color_errors =
    None, r_id=None, z_id=None):
        """Create a galaxy object using the information passed in."""
        self.ra = float(ra)
        self.dec = float(dec)
        self.mags = dict()
        self.mag_residuals = dict()
        self.colors = dict()
        self.r_id = r_id
        self.z_id = z_id
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
        for band1 in self.mags:
            for band2 in self.mags:
                if not band1 == band2:
                    self.colors[band1 + "-" + band2] = self.mags[band1] - self.mags[band2]
                    # That line does the error things automatically, since noth mags are data objects


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

class Predictions(object):
    """
    Class storing data from the EzGal models.
    """
    def __init__(self, redshift, r_mag, i_mag, z_mag, ch1_mag, ch2_mag, slope):
        """
        Initialize the predictions object, using the given data.

        :param redshift: redshift where all the other values apply
        :param r_mag: Sloan r band magnitude
        :param i_mag: Sloan i band magnitude
        :param z_mag: Sloan z band magnitude
        :param ch1_mag: IRAC ch1 magnitude
        :param ch2_mag: IRAC ch2 magnitude
        :param slope: slope of the red sequence
        :return: Predictions object
        """
        self.redshift = redshift
        self.r_mag = r_mag
        self.i_mag = i_mag
        self.z_mag = z_mag
        self.ch1_mag = ch1_mag
        self.ch2_mag = ch2_mag
        # function assigns slope itself
        self. rz_line = self._make_line(slope, self.z_mag, self.r_mag - self.z_mag)

    def _make_line(self, slope, l_star_mag, l_star_color):
        """
        Makes the line that represents the red sequence.

        :param slope: slope of the red sequence
        :param l_star_mag: characteristic magnitude
        :param l_star_color: characteristic color
        :return: none, but line is assigned within the function
        """
        # Now make more points that form a the x values of the line
        xs = np.arange(l_star_mag - 10, l_star_mag + 10, 0.01).tolist()
        # round the x values
        xs = [round(x, 2) for x in xs]

        # Turn this data to a line object, and assign that to the instance attribute
        return Line(xs, slope=slope, x_point=l_star_mag, y_point=l_star_color)


class Line(object):
    """
    Class that holds data for lines. This makes handling the line data easier, especially for predictions
    """

    def __init__(self, xs=None, ys=None, slope=None, x_point=None, y_point=None):
        """Makes the line object. Can either be passed a pre-made line, or a point and the slope.

        Two ways to pass in data:
            1. pass in two lists: one for x values, and one for y values. They need to be the same length.
            2. Pass in the slope, and a point. The point slope formula will be used to turn it into x and y values.

        :param xs: list of x values
        :param ys: list of y values
        :param slope: slope of the line
        :param x_point: x value of a point on the line
        :param y_point: y value of the point on the line
        :return:
        """
        if xs and ys:
            if len(xs) == len(ys):
                self.xs = xs
                self.ys = ys
            else:
                print "X and Y lists need to be the same length. Try again. Nothing is made."
        elif xs and slope and x_point and y_point:
            # Use a rearranged point slope form to find the equation for the line
            # y-y1 = m(x-x1)
            # y = m*x - m*x1 + y1
            # where m=slope, x1=x_point, y1=y_point
            self.xs = xs
            self.ys = [slope*x - slope*x_point + y_point for x in xs]


class EndProgramError(Exception):
    """Exception class that ends the program when raised. Prints an error message,
    as well as optionally printing a value that caused the exception.
    """
    def __init__(self, message, offending_value=None):
        print message
        if offending_value:
            print "Here is the offending value: " + str(offending_value)
        raise Exception  # Exits the program