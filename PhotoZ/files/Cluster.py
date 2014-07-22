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

    # TODO: Set this to work without bootstrapping, and instead with chi-squared interval sigma estimation

    def fit_z(self, plot_figures=None):
        """Find the redshift of the cluster by matching its red sequence to the models.
        Basically works as the main function for this process. Other functions are called to do the dirty work.

        :param plot_figures: To plot figures, pass in a list that the figures will be appended to.
                             If no plotting is desired, leave the parameter blank (i.e. pass nothing in).
        :return: None, but the instance variables for photometric redshift and photo z error are set inside.
        """
        # Find a good starting redshift to base the rest of the work on, and set RS membership
        initial_z = self._find_initial_redshift(plot_bar=True)

        bluer_color_cut = [-0.30, -0.25, -0.20]
        redder_color_cut = [0.4, 0.3, 0.2]
        brighter_mag_cut = -1.4
        dimmer_mag_cut = 0.6
        self._set_as_rs_member(self.galaxy_list, initial_z, bluer_color_cut[0], redder_color_cut[0],
                               brighter_mag_cut, dimmer_mag_cut)

        # If plot_figures is a list, plot and append. If nothing was passed in, this will not trigger.
        if type(plot_figures) is list:
            # Plot with predictions
            plot_figures.append(plotting.plot_color_mag(self, predictions=True, distinguish_red_sequence=False))
            # Need [0] since the function returns figure and axes objects, and [0] gives just the figure.
            # Plot the initial cut with RS based on the initial cut
            plot_figures.append(plotting.plot_fitting_procedure(self, initial_z, other_info="Initial Fitting",
                                                                color_red_sequence=False))
            # Plot location of initial cut
            # plot_figures.append(plotting.plot_location(self))

        # Want to do three decreasing sized color cuts around the best fit redshift so far, to gradually hone in on
        # the correct redshift.

        best_z = initial_z
        z_error = 999
        for i in range(len(bluer_color_cut)):

            # Use the bootstrapping method to find the best fit redshift within the color cut specified.
            # First need to set RS memebers
            self._set_as_rs_member(self.galaxy_list, best_z, bluer_color_cut[i], redder_color_cut[i],
                                   brighter_mag_cut, dimmer_mag_cut)

            # Plot most recent redshift estimate
            plot_figures.append(plotting.plot_fitting_procedure(self, best_z, other_info="Cut " + str(i+1)))

            #best_z, z_error = self._bootstrap(best_z, plot_figures) # Plot process
            best_z, z_error = self._bootstrap(best_z)  # No plotting of process




        # Set cluster attributes, now that the process is complete
        self.photo_z = best_z
        self.photo_z_error = z_error


        # Plot final redshift on CMD
        if type(plot_figures) is list:
            plot_figures.append(plotting.plot_fitting_procedure(self, self.photo_z, "Final Redshift",
                                                                color_red_sequence=False))
            # plot_figures.append(plotting.plot_location(self))

    def _find_initial_redshift(self, plot_bar=True):
        """Find a good redshift for the cluster, based on the highest number of galaxies near a predicted RS line.

        Iterates through all redshifts, and counts the number of galaxies within 0.1 color of the model line. Then
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
            rs_members = 0
            self._set_as_rs_member(self.galaxy_list, z, -0.1, 0.1, -2.0, 0.5)
            for gal in self.galaxy_list:
                if gal.RS_member:
                    rs_members += 1

            # Append the results to lists
            galaxies_list.append(rs_members)
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

        whole_sample = [gal for gal in self.galaxy_list if gal.RS_member]
        z_list = []

        for i in range(0, 100):
            # Create a new random sample, find it's photometric redshift, and append it to a list
            random_resample = main_functions.sample_with_replacement(whole_sample, len(whole_sample))
            this_z = self._fit_redshift(random_resample)
            if type(figs) is list:
                figs.append(plotting.plot_fitting_procedure(self, this_z, other_info="iteration" + str(i+1)))
            z_list.append(this_z)

        # the numpy median and standard deviation functions don't play nice with strings, so we need to make them floats
        float_z_list = [float(z) for z in z_list]
        # The photometric redshift should still be in string format, again to avoid floating point errors with dict keys
        photo_z = str(round(np.median(float_z_list), 2))
        photo_z_error = np.std(float_z_list)  # Is fine as a float
        return photo_z, photo_z_error

    def _fit_redshift(self, galaxies):
        # TODO: Document
        # set placeholders
        best_chi_squared = 999
        best_z = 999
        for z in sorted(self.predictions_dict.iterkeys()):  # redshifts in order, so we can look at chi distribution
            temp_chi_squared = main_functions.simple_chi_square(galaxies, self.predictions_dict[z].rz_line)
            if temp_chi_squared < best_chi_squared:
                best_z = z
                best_chi_squared = temp_chi_squared
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
