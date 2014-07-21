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

    def __init__(self, galaxy_list, name, filters, spec_z=None):
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
        # Real objects won't have spectroscopic redshifts, so set to none
        if spec_z:
            self.spec_z = str(spec_z)  # Strings are easier to deal with that floats for this usage.
        else:
            self.spec_z = None
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
        # Find a good starting redshift to base the rest of the work on, and set RS membership
        initial_z = self._find_initial_redshift(plot_bar=False)
        self._set_as_rs_member(self.galaxy_list, initial_z, -0.3, 0.8, bright_mag_cut=-1.5, faint_mag_cut=0.6)

        # If plot_figures is a list, plot and append. If nothing was passed in, this will not trigger.
        if type(plot_figures) is list:
            # Plot with predictions
            plot_figures.append(plotting.plot_color_mag(self, predictions=True, distinguish_red_sequence=False))
            # Need [0] since the function returns figure and axes objects, and [0] gives just the figure.
            # Plot the initial cut
            plot_figures.append(plotting.plot_fitting_procedure(self, initial_z, "Initial Fitting"))
            # Plot location of initial cut
            plot_figures.append(plotting.plot_location(self))

        # Use the bootstrapping method to refine the redshift estimation
        self._bootstrap(initial_z, plot_figures)

        # Plot final redshift on CMD
        if type(plot_figures) is list:
            plot_figures.append(plotting.plot_fitting_procedure(self, self.photo_z, "Final Redshift"))
            plot_figures.append(plotting.plot_location(self))

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
                if self.predictions_dict[z].z_mag - 1.2 < gal.mag < self.predictions_dict[z].z_mag + 0.7 \
                        and gal.color_error < 0.2:
                    idx = self.predictions_dict[z].rz_line.xs.index(gal.mag)
                    # If it's within color cut, increment counter
                    if abs(self.predictions_dict[z].rz_line.ys[idx] - gal.color) < 0.10:
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
        self._set_as_rs_member(self.galaxy_list, initial_z, -0.3, 0.8, -1.5, 0.6)
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
        self.photo_z_error = np.std(float_z_list)  # Is fine as a float

        # Set RS membership to final redshift
        self._set_as_rs_member(self.galaxy_list, self.photo_z, -0.15, 0.4, -1.5, 0.6)

    def _find_rs_redshift(self, initial_z, galaxies, figures=None):
        """Use an iterative process to find the best redshift for the given galaxies in the red sequence.

        The galaxies passed in will be cut down with a color cut around the initial redshift, then a new redshift will
        be fit to these galaxies. Then a smaller color cut will be applied around this new redshift, and another
        redshift will be fitted. This process will be repeated 3 times, which should be enough time for the fit to
        converge on the correct redshift for the given galaxies.

        :param initial_z: redshift the cut will be made around. Where the fitting starts.
        :param galaxies: List of galaxies that will be fit by a red sequence prediction for redshift.
        :param figures: List or not, where plots will be appended. Pass a list in to plot. If nothing is passed into
        this parameter, the process of fitting will not be plotted.
        :return: redshift that provides the best red sequence fit to the galaxies passed in.
        """

        best_z = initial_z

        lower_color_cut = [-0.2, -0.15, -0.15]
        upper_color_cut = [0.6, 0.5, 0.4]
        # Will use 3 iterations of smaller cuts. Too few will not find the RS correctly, while too many will take
        #  a long time to run. Hopefully this is a good balance.
        for i in range(len(lower_color_cut)):
            # Keep track of the redshift for this iteration, will use it to restrict which redshifts we test
            intermediate_z = best_z

            # Set galaxies as RS members if they are within the color cut, and make that the sample
            self._set_as_rs_member(galaxies, best_z, lower_color_cut[i], upper_color_cut[i])
            sample = [gal for gal in galaxies if gal.RS_member]

            # Now we can do the fitting on this sample.
            best_chi_squared = 314159  # I used this distinctive value so if it doesn't get replaced, I can tell
            for z in self.predictions_dict:
                # Only want to test redshifts that are close to most recent guess, to not waste time
                if abs(float(intermediate_z) - float(z)) < 0.15:
                    temp_chi_squared = main_functions.simple_chi_square(sample, self.predictions_dict[z].rz_line)
                    if temp_chi_squared < best_chi_squared:
                        best_z = z
                        best_chi_squared = temp_chi_squared

            if type(figures) is list:  # Plot if we want to plot
                figures.append(plotting.plot_fitting_procedure(self, best_z, "cut " + str(i + 1)))

        if float(best_z) > 1.5:  # Something went wrong , so print helpful info
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

    def _set_as_rs_member(self, galaxies, redshift, bluer_color_residual_cut, redder_color_residual_cut,
                          bright_mag_cut=-999.9,  faint_mag_cut=999.9):
        """Set certain galaxies as red sequence members if they meet magnitude and color cuts.

        :param galaxies: list of galaxies to be tested for RS membership
        :param redshift: Redshift of the red sequence.
        :param bluer_color_residual_cut: How many magnitudes brighter than the characteristic magnitude of the RS
               galaxies can still be considered RS members.
        :param redder_color_residual_cut: How many magnitudes fainter than the characteristic magnitude galaxies will
               still be considered RS.
        :param bright_mag_cut: How many magnitudes bluer than the characteristic color a galaxy can be
        :param faint_mag_cut:
        :return: none, but sets instance attributes of galaxies
        """

        # First set all galaxies as not RS members
        for gal in self.galaxy_list:
            gal.RS_member = False

        self._set_residuals(redshift)
        for gal in galaxies:
            if (self.predictions_dict[redshift].z_mag + bright_mag_cut < gal.mag <
                    self.predictions_dict[redshift].z_mag + faint_mag_cut and
                    bluer_color_residual_cut < gal.color_residual < redder_color_residual_cut):
                gal.RS_member = True

    def _set_residuals(self, redshift):
        """
        Set each galaxy's color_residual instance attribute to the difference between the predicted RS color and the
        galaxy's color.

        :return: none, but instance attributes are changed in galaxy objects.
        """

        best_z_line = self.predictions_dict[redshift].rz_line
        for gal in self.galaxy_list:
            if 18 < gal.mag < 30:  # The line used doesn't extend beyond these points.
                idx = best_z_line.xs.index(gal.mag)
                gal.color_residual = gal.color - best_z_line.ys[idx]
            else:
                gal.color_residual = 999
