from PhotoZ.files import main_functions
from PhotoZ.files import plotting
import numpy as np


class Cluster(object):
    """Class representing one cluster, and that holds all the data about the cluster.

    Has a list of galaxies in the image of the cluster, which are stored as galaxy objects. Also holds information
    about the name of the cluster, the filters used to take the image, and its spectroscopic and photometric redshifts.

    The photometric redshifts are calculated using the fit_z function.
    """

    # Keeping the predictions for the red sequence with the cluster object made things a lot easier. And since the
    # predictions are the same for all cluster, this is a class variable rather than an instance variable.
    predictions_dict = main_functions.make_prediction_dictionary(0.01)

    def __init__(self, galaxy_list, name, filters, spec_z):
        """
        Creates a new cluster object, holding the list of galaxies within it
        :param galaxy_list: list of galaxy objects
        :param name: Name of the cluster
        :param filters: list of filters used to image the cluster
        :param spec_z: spectroscopic redshift of the cluster. Pass in as a string!
        :return: cluster object
        """
        self.galaxy_list = galaxy_list
        self.name = name
        self.filters = filters
        self.spec_z = str(spec_z)
        self.photo_z = 0.0
        self.photo_z_error = 0.0

    def __repr__(self):
        return self.name + "; spec z = " + str(self.spec_z)

    def fit_z(self, plot_figures=None):
        """Find the redshift of the cluster by matching its red sequence to the models.
        Basically works as the main function for this process. Other functions are called to do the dirty work.

        :param plot_figures: To plot figures, pass in a list that the figures will be appended to.
                             If no plotting is desired, leave the parameter blank (i.e. pass nothing in).
        :return: None, but the instance variables for photometric redshift and photo z error are set inside.
        """
        # Find a good starting redshift to base the rest of the work on.
        initial_z = self._find_initial_redshift(plot_bar=False)

        # Define the initial red sequence as galaxies within 5 sigma of this initial redshift.
        self._set_as_rs_member(self.galaxy_list, initial_z, 5.0)
        # If plot_figures is a list, plot and append. If nothing was passed in, this will not trigger.
        if type(plot_figures) is list:
            # Plot the initial cut
            plot_figures.append(plotting.plot_fitting_procedure(self, initial_z, "Initial Fitting (5 sigma cut)"))

        # Use the bootstrapping method to refine the redshift estimation
        self._bootstrap(initial_z, plot_figures)

        # Plot final redshift on CMD
        # For looks, set all galaxies to not be RS members
        for gal in self.galaxy_list:
            gal.RS_member = False
        if type(plot_figures) is list:
            plot_figures.append(plotting.plot_fitting_procedure(self, self.photo_z, "Final Redshift"))

    def _find_initial_redshift(self, plot_bar=True):
        """Find a good redshift for the cluster, based on the highest number of galaxies near a predicted RS line.

        Iterates through all redshifts, and counts the number of galaxies within 1.5 sigma of the model line. Then
        the redshift that has the highest number of galaxies (including some contributions from neighboring
        redshifts) is the redshift selected. This redshift is not necessarily the best fit, just a good starting
        place for more sophisticated fitting.

        :param plot_bar: Whether or not to make a bar graph showing the number of galaxies near each redshift.
        :return: best fitting redshift.
        """
        # Initialize empty lists, will append as we go
        galaxies_list = []
        z_list = []

        # Iterate through each redshift we have predictions for
        for z in sorted(self.predictions_dict.iterkeys()):  # need to be sorted, since we will be including neighbors
            galaxies = 0
            # For each galaxy, find out whether it would be a RS member if the cluster is at that redshift
            for gal in self.galaxy_list:
                # Simple magnitude cut that is where the RS will be, along with error limits
                if self.predictions_dict[z].z_mag - 1.2 < gal.mag < self.predictions_dict[z].z_mag + 0.8 \
                        and gal.color_error < 0.5:
                    idx = self.predictions_dict[z].rz_line.xs.index(gal.mag)
                    # If it's within 1.5 sigma, increment galaxy counter
                    if abs((self.predictions_dict[z].rz_line.ys[idx] - gal.color) / gal.color_error) < 1.5:
                        galaxies += 1

            # Append the results to lists
            galaxies_list.append(galaxies)
            z_list.append(z)

        # The best redshift will be the one with the most RS galaxies. Since the data is noisy, adding the 3 neighbors
        # on each side will make for more stable results
        highest_sum = 0
        best_z = 0
        for k in range(3, len(z_list)-3):  # Can't start at 0, since we need 3 neighbors on each side
            temp_sum = (galaxies_list[k-3] + galaxies_list[k-2] + galaxies_list[k-1] + galaxies_list[k] +
                        galaxies_list[k+1] + galaxies_list[k+2] + galaxies_list[k+3])
            if temp_sum > highest_sum:
                highest_sum = temp_sum
                best_z = z_list[k]

        if plot_bar:
            plotting.plot_initial_redshift_finding(self, z_list, galaxies_list, best_z)

        return best_z

    def _bootstrap(self, initial_z, figs=None):
        """Use bootstrapping resampling with replacement to estimate the best photometric redshift for the cluster.

        Does 100 iterations, where the redshift is calculated on each random resample with replacement. The mean
        value of these 100 redshifts will be the cluster's redshift, and the standard deviation of the redshifts is
        the error.

        :param initial_z: Redshift where the process starts. Is passed to the _find_rs_redshift function, which uses
                          it more than this function.
        :return: None. Does set the instance variables of this cluster for the photometric redshift, along with its
                 error.
        """
        # Need to define an initial sample, so we can resample from it later.
        whole_sample = [gal for gal in self.galaxy_list if gal.RS_member]
        z_list = []

        for i in range(0, 100):
            # Create a new random sample, find it's photometric redshift, and append it to a list
            random_resample = main_functions.sample_with_replacement(whole_sample, len(whole_sample))
            #this_z = self._find_rs_redshift(initial_z, random_resample, figs)  # To plot fitting procedure
            this_z = self._find_rs_redshift(initial_z, random_resample)  # No plotting of fitting procudure
            z_list.append(this_z)

        # the numpy median and standard deviation functions don't play nice with strings, so we need to make them floats
        float_z_list = [float(z) for z in z_list]
        # The photometric redshift should still be in string format, again to avoid floating point errors with dict keys
        self.photo_z = str(round(np.median(float_z_list), 2))
        # TODO: Find what the correct error would be. I don't think this is right.
        self.photo_z_error = np.std(float_z_list)  # Is fine as a float

    def _find_rs_redshift(self, initial_z, galaxies, figures=None):
        """Do an iterative process to find the best fit redshift to the given galaxies.

        Calculated the best fit redshift to galaxies within 5 sigma of the initial redshift. Then the fit is found on
        galaxies within 4 sigma of the redshift found for the 5 sigma sample. Then the sample is restricted to 3 sigma
        from the redshift from 4 sigma, and that redshift is the final redshift.

        :param initial_z: Redshift that is a rough estimate. Fitting will start from here.
        :param galaxies: List of galaxies to be fitted by a redshift.
        :param figures: List of figures that plots will be appended to. Can be None if no plots are desired.
        :return:
        """
        best_z = initial_z  # We have to start somewhere
        # Want to have an iterative process, where the cut gradually gets closer to the current best line
        for sigma in range(5, 2, -1):  # Will go 5, 4, 3
            # Define the red sequence as galaxies within the desired sigma
            self._set_as_rs_member(galaxies, best_z, sigma)
            # Make the sample out of just the RS galaxies we just defined
            sample = [gal for gal in galaxies if gal.RS_member]

            # Set placeholders that will be replaced as the code runs (hopefully)
            best_chi_squared = 314159
            best_z = 314159
            # for all redshifts, calculate the chi squared, and replace placeholders if it's better than the current.
            for z in self.predictions_dict:
                temp_chi_squared = main_functions.simple_chi_square(sample, self.predictions_dict[z].rz_line)
                if temp_chi_squared < best_chi_squared:
                    best_z = z
                    best_chi_squared = temp_chi_squared

            if type(figures) is list:  # Plot if we want to plot
                figures.append(plotting.plot_fitting_procedure(self, best_z, str(sigma) + " sigma"))
        if float(best_z) > 1.5:  # Something went wrong, so print helpful info
            print "\n#############################################\n"
            print "Something went wrong with the fitting procedure once"
            print "Best z =", best_z
            print "Best chi squared", best_chi_squared
            print "Started at z =", initial_z
            print "Cluster's spec z =", self.spec_z
            print "Sample has length:", len(sample)
            print "Here's the whole sample"
            print sample
            print "#################################################\n"

        return best_z

    def _set_as_rs_member(self, galaxies, redshift, sigma):
        """Sets the galaxy instance attribute if the galaxy is within a certain sigma of the red sequence.

        Uses a magnitude cut around the characteristic magnitude, as well as a sigma cut around the color at the
        galaxy's magnitude. The sigma calculation includes the RS spread.
        :param galaxies: List of galaxies that will be tested for RS membership.
        :param redshift: Redshift at which the galaxies will be tested for RS membership.
        :param sigma: Limit at which galaxies will be considered part of the RS.
        :return: none, but the galaxy instance attributes will be changed.
        """

        # Set all galaxies as not RS first, so any galaxies not passed into the function will be not RS.
        for galaxy in self.galaxy_list:
                galaxy.RS_member = False
        for gal in galaxies:
            # If they are in a magnitude cut around L*
            if self.predictions_dict[redshift].z_mag - 2.0 < gal.mag < self.predictions_dict[redshift].z_mag + 0.8:
                # Find the place we can find the predicted color.
                idx = self.predictions_dict[redshift].rz_line.xs.index(gal.mag)
                # If it's within 2 sigma, it's a member
                if main_functions.calculate_sigma(gal, self.predictions_dict[redshift].rz_line.ys[idx]) < sigma:
                    gal.RS_member = True
                else:
                    gal.RS_member = False
        # TODO: Plot locations of the members. See if there is clustering in the very center.

    def set_residuals(self):
        """
        Set each galaxy's color_residual instance attribute to the difference between the predicted RS color and the
        galaxy's color.

        :return: none, but instance attributes are changed in galaxy objects.
        """

        best_z_line = self.predictions_dict[self.photo_z].rz_line
        for gal in self.galaxy_list:
            if 18 < gal.mag < 30:  # The line used doesn't extend beyond these points.
                idx = best_z_line.xs.index(gal.mag)
                gal.color_residual = gal.color - best_z_line.ys[idx]
            else:
                gal.color_residual = 999