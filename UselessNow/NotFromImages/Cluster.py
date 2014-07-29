import math

import numpy as np

from UselessNow.NotFromImages import main_functions
from UselessNow.NotFromImages import plotting


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
        self.upper_photo_z_error = 0.0
        self.lower_photo_z_error = 0.0



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
        if type(plot_figures) is list:
            plot_figures.append(plotting.plot_color_mag(self, predictions=False))

        # if "G" in self.name:
        if True:
            plot_figures.append(self._find_location_cut())
            # self._find_location_cut()

        initial_z = self._find_initial_redshift(plot_bar=True)

        bluer_color_cut = [-0.30, -0.25, -0.20]
        if self.name.startswith("MOO1636"):
            bluer_color_cut = [-0.2, -0.2, -0.2]  # Override to avoid "foregrounds." Not sure if actually foregrounds
        redder_color_cut = [0.4, 0.3, 0.2]
        brighter_mag_cut = -1.4
        dimmer_mag_cut = 0.6
        self._set_as_rs_member(self.galaxy_list, initial_z, bluer_color_cut[0], redder_color_cut[0],
                               brighter_mag_cut, dimmer_mag_cut)

        # If plot_figures is a list, plot and append. If nothing was passed in, this will not trigger.
        if type(plot_figures) is list:
            # Plot with predictions
            plot_figures.append(plotting.plot_color_mag(self, predictions=True, distinguish_red_sequence=False))
            # Plot the initial cut with RS based on the initial cut
            plot_figures.append(plotting.plot_fitting_procedure(self, initial_z, other_info="Initial Fitting",
                                                                color_red_sequence=False))
            # Plot location of initial cut
            plot_figures.append(plotting.plot_location(self))
            pass  # So when I comment all the plots out it still runs



        # Want to do three decreasing sized color cuts around the best fit redshift so far, to gradually hone in on
        # the correct redshift.

        best_z = initial_z
        z_upper_error, z_lower_error = 999, 999
        for i in range(len(bluer_color_cut)):

            # Use the bootstrapping method to find the best fit redshift within the color cut specified.
            # First need to set RS memebers
            self._set_as_rs_member(self.galaxy_list, best_z, bluer_color_cut[i], redder_color_cut[i],
                                   brighter_mag_cut, dimmer_mag_cut)
            sample = [gal for gal in self.galaxy_list if gal.RS_member]

            # Plot most recent redshift estimate
            plot_figures.append(plotting.plot_fitting_procedure(self, best_z, other_info="Cut " + str(i+1)))

            chi_redshift_list = self._fit_redshift_to_sample(sample)

            best_z, z_lower_error, z_upper_error = self._get_stats_from_chi(chi_redshift_list)




        # Set cluster attributes, now that the process is complete
        self.photo_z = best_z
        self.upper_photo_z_error = z_upper_error
        self.lower_photo_z_error = z_lower_error
        print "upper:", z_upper_error, "lower:", z_lower_error

        # Make final RS cut, which will be slightly larger than the cut used to identify the RS
        self._set_as_rs_member(self.galaxy_list, self.photo_z, -0.3, 0.6, -1.2, 1.0)
        # Override for lower redshift struture, since there is a higher structure that gets in the way
        if self.name.startswith("MOO2214"):
            self._set_as_rs_member(self.galaxy_list, self.photo_z, -0.2, 0.2, -1.2, 0.8)
        if self.name.startswith("MOO1636"):
            self._set_as_rs_member(self.galaxy_list, self.photo_z, -0.3, 0.6, -1.6, 1.0)


        # Plot final redshift on CMD
        if type(plot_figures) is list:
            plot_figures.append(plotting.plot_fitting_procedure(self, self.photo_z, "Final Redshift",
                                                                color_red_sequence=True))
            plot_figures.append(plotting.plot_location(self))

        self._write_rs_catalog()


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
            self._set_as_rs_member(self.galaxy_list, z, -0.1, 0.1, -1.4, 0.5)  # 3rd spot could be -2.0
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

    def _fit_redshift_to_sample(self, galaxies):
        # TODO: Document
        # set placeholders
        chi_squared_redshift_pairs = []
        for z in sorted(self.predictions_dict.iterkeys()):  # redshifts in order, so we can look at chi distribution
            temp_chi_squared = main_functions.simple_chi_square(galaxies, self.predictions_dict[z].rz_line)
            chi_squared_redshift_pairs.append((z, temp_chi_squared))

        return chi_squared_redshift_pairs

    def _get_stats_from_chi(self, chi_redshift_pairs, figs=None):
        # TODO: Document

        best_chi = 999
        best_z = 999
        for pair in chi_redshift_pairs:
            if pair[1] < best_chi:
                best_z = pair[0]
                best_chi = pair[1]

        # now find error limits
        left_limit = 1.6
        right_limit = 0.4
        for pair in chi_redshift_pairs:
            if pair[1] < best_chi + 1.0:  # Within one sigma
                if float(pair[0]) < float(best_z):  # Will be left limit
                    if float(pair[0]) < left_limit:
                        left_limit = float(pair[0])
                else:  # Will be right limit
                    if float(pair[0]) > right_limit:
                        right_limit = float(pair[0])

        if type(figs) is list:
            figs.append(plotting.plot_chi_data(self, chi_redshift_pairs, left_limit, best_z, right_limit))
        lower_error = float(best_z) - float(left_limit)
        upper_error = float(right_limit) - float(best_z)
        return best_z, lower_error, upper_error

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

    def _find_location_cut(self):
        self.all_galaxies = self.galaxy_list

        median_ra = np.median([gal.ra for gal in self.galaxy_list])
        median_decs = np.median([gal.dec for gal in self.galaxy_list])

        # Override for one cluster
        if self.name.startswith("MOO1636"):
            median_decs += 0.008  # best so far is 0.008
            median_ra += 0.005  # best so far is 0.005
        print median_ra, median_decs

        gals_in_location = []

        for gal in self.galaxy_list:
            dist = math.sqrt((gal.ra - median_ra)**2 + (gal.dec - median_decs)**2)
            if self.name.startswith("MOO2214"):
                # For more distant MOO2214, use 0.0 < 1.0
                # for less distant MOO2214, use 0.0 < 2.0
                if dist < 1.0/60.0:
                    gals_in_location.append(gal)
                    gal.RS_member = True
            if self.name.startswith("MOO1636"):
                # best for MOO1636: 0 < 1.3
                if dist < 1.3/60.0:
                    gals_in_location.append(gal)
                    gal.RS_member = True
        fig = plotting.plot_location(self)

        self.galaxy_list = gals_in_location
        return fig

    def _write_rs_catalog(self):
        # TODO: Document
        # write red sequence catalog to file
        rs_catalog = open("/Users/gbbtz7/Desktop/" + self.name[:-1] +
                          "_rs_members.phot.cat", "w")
        rs_catalog.write("# id    ra            dec          zmag     rmz    rmze        rs_member\n")
        for gal in self.galaxy_list:
            if gal.RS_member:
                rs_catalog.write(str(gal.id) + "    " + str(gal.ra) + "    " + str(gal.dec) + "    " + str(gal.mag) +
                                 "    " + str(gal.color) + "    " + str(gal.color_error) + "    " + "1" + "\n")
            else:
                rs_catalog.write(str(gal.id) + "    " + str(gal.ra) + "    " + str(gal.dec) + "    " + str(gal.mag) +
                                 "    " + str(gal.color) + "    " + str(gal.color_error) + "    " + "0" + "\n")
        rs_catalog.close()


