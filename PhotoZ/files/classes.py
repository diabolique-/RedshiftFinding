import numpy as np
import decimal


class Galaxy(object):
    """Class representing a galaxy. Has data members for everything contained in the data files."""

    def __init__(self, id_num, ra, dec, mag, color, color_error):
        """Create a galaxy object using the information passed in."""
        self.id = int(id_num)
        self.ra = float(ra)
        self.dec = float(dec)
        self.mag = float(mag)
        self.color = float(color)
        self.color_error = float(color_error)
        self.color_residual = 0.0
        self.RS_member = False


class Image(object):
    """
    Class representing one image, and that holds all the data contained within that image.
    """
    def __init__(self, galaxy_list, name, filters, spec_z):
        """
        Creates a new image object, holding the list of galaxies within it
        :param galaxy_list: list of galaxy objects
        :param name: Title of the image.
        :param filters: list of filters used in this image
        :param spec_z: spectroscopic redshift of the cluster in this image. Pass in as a string!
        :return: image object
        """
        self.galaxy_list = galaxy_list
        self.name = name
        self.filters = filters
        self.spec_z = decimal.Decimal(spec_z)
        self.photo_z = 0
        self.photo_z_error = 0.0

    def __repr__(self):
        return self.name + "; spec z = " + str(self.spec_z)


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
        self._make_rs_rz(slope, self.z_mag, self.r_mag - self.z_mag)

    def _make_rs_rz(self, slope, l_star_mag, l_star_color):
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
        self.rz_line = Line(xs, slope=slope, x_point=l_star_mag, y_point=l_star_color)


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

