from PhotoZ.files import plotting
from PhotoZ.files import predictions
import numpy as np
import math

class Cluster(object):
    """

    """
    # tODO: document
    # Keeping the predictions for the red sequence with the cluster object made things a lot easier. And since the
    # predictions are the same for all cluster, this is a class variable rather than an instance variable.
    predictions_dict = predictions.make_prediction_dictionary(0.01)

    def __init__(self, name, sources_list, spec_z=None):
        # TODO: document
        # Assign the cluster's name, and the spectroscopic redshift, if it exists.
        self.name = name
        if spec_z:
            self.spec_z = spec_z
        else:
            self.spec_z = None

        self.sources_list = sources_list

        self.r_data = False
        self.i_data = False
        self.z_data = False
        self.ch1_data = False
        self.ch2_data = False
        self.photo_z = dict()

    def __repr__(self):  # how the object appears when printed
        return self.name

    def calculate_color(self):
        for source in self.sources_list:
            source.calculate_color()




    ######################################

    # Documentation needed below this line

    #######################################


    def fit_z(self, color, plot_figures=None):
        """Find the redshift of the cluster by matching its red sequence to the models.
        Basically works as the main function for this process. Other functions are called to do the dirty work.

        :param color: str with the color that the fitting procedure will be done with. Should be in the format
        "band1-band2" (like "r-z")
        :param plot_figures: To plot figures, pass in a list that the figures will be appended to.
                             If no plotting is desired, leave the parameter blank (i.e. pass nothing in).
        :return: None, but the instance variables for photometric redshift and photo z error are set inside.
        """
        # Find a good starting redshift to base the rest of the work on, and set RS membership



        # if type(plot_figures) is list:
        #     plot_figures.append(plotting.plot_color_mag(self, predictions=False, color=color, band=color[-1]))

        print self.name

        if "z" not in self.name:
            # plot_figures.append(self._find_location_cut())
            self._find_location_cut(1.5)



        initial_z = self._find_initial_redshift(color, plot_bar=True)


        bluer_color_cut = [-0.30, -0.25, -0.20]
        if self.name.startswith("MOO1636"):
            bluer_color_cut = [-0.2, -0.2, -0.2]  # Override to avoid "foregrounds." Not sure if actually foregrounds
        redder_color_cut = [0.4, 0.3, 0.2]
        brighter_mag_cut = -1.4
        dimmer_mag_cut = 0.6


        self._set_as_rs_member(self.sources_list, initial_z, color, bluer_color_cut[0], redder_color_cut[0],
                               brighter_mag_cut, dimmer_mag_cut)



        # If plot_figures is a list, plot and append. If nothing was passed in, this will not trigger.
        if type(plot_figures) is list:
            # Plot with predictions
            # plot_figures.append(plotting.plot_color_mag(self, color, band=color[-1], predictions=True,
            #                                             distinguish_red_sequence=False))
            # # Plot the initial cut with RS based on the initial cut
            # plot_figures.append(plotting.plot_fitting_procedure(self, color, color[-1], initial_z, other_info="Initial "
            #                                                     "Fitting", color_red_sequence=False))
            # # Plot location of initial cut
            # plot_figures.append(plotting.plot_location(self))
            pass  # So when I comment all the plots out it still runs



        # Want to do three decreasing sized color cuts around the best fit redshift so far, to gradually hone in on
        # the correct redshift.

        best_z = initial_z
        z_upper_error, z_lower_error = 999, 999
        for i in range(len(bluer_color_cut)):

            # First need to set RS memebers
            self._set_as_rs_member([source for source in self.sources_list if source.in_location], best_z, color,
                                   bluer_color_cut[i],
                                   redder_color_cut[i],
                                   brighter_mag_cut, dimmer_mag_cut)
            sample = [source for source in self.sources_list if source.RS_member]

            if len(sample) < 3:  # TODO: remove this once calibration is fixed
                return

            # Plot most recent redshift estimate
            # plot_figures.append(plotting.plot_fitting_procedure(self, color, color[-1], best_z, other_info="Cut " + str(
            #     i+1)))

            chi_redshift_list = self._fit_redshift_to_sample(sample, color, color[-1])

            best_z, z_lower_error, z_upper_error = self._get_stats_from_chi(chi_redshift_list)




        # Set cluster attributes, now that the process is complete
        self.photo_z[color] = best_z
        self.upper_photo_z_error = z_upper_error
        self.lower_photo_z_error = z_lower_error

        # Make final RS cut, which will be slightly larger than the cut used to identify the RS
        self._set_as_rs_member(self.sources_list, self.photo_z[color], color, -0.3, 0.6, -1.2, 1.0)
        # self._set_as_rs_member([source for source in self.sources_list if source.in_location], self.photo_z, color, -0.3, 0.6,
        #                        -1.2, 1.0)
        # Override for lower redshift struture, since there is a higher structure that gets in the way
        # if self.name.startswith("MOO2214"):
        #     self._set_as_rs_member(self.sources_list, self.photo_z[color], color, -0.2, 0.2, -1.2, 0.8)
        # if self.name.startswith("MOO1636"):
        #     self._set_as_rs_member(self.sources_list, self.photo_z[color], color, -0.3, 0.6, -1.6, 1.0)


        # Plot final redshift on CMD
        if type(plot_figures) is list:
            plot_figures.append(plotting.plot_fitting_procedure(self, color, color[-1], self.photo_z[color],
                                                                "Final Redshift",
                                                                color_red_sequence=True))
            plot_figures.append(plotting.plot_location(self))

        print self, self.photo_z[color]


        # self._write_rs_catalog()


    def _find_initial_redshift(self, color, plot_bar=True):
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
            self._set_as_rs_member(self.sources_list, z, color, -0.1, 0.1, -1.4, 0.5)  # 3rd spot could be -2.0
            for source in self.sources_list:
                if source.RS_member:
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

        if best_z == 0:
            best_z = "0.5"  # TODO: get rid of this once I correct calibration

        return best_z

    def _fit_redshift_to_sample(self, galaxies, color, band):
        # TODO: Document
        # set placeholders
        chi_squared_redshift_pairs = []
        for z in sorted(self.predictions_dict.iterkeys()):  # redshifts in order, so we can look at chi distribution
            temp_chi_squared = predictions.simple_chi_square(galaxies, color, band, self.predictions_dict[
                z].rz_line)
            chi_squared_redshift_pairs.append((z, temp_chi_squared))

        return chi_squared_redshift_pairs

    def _get_stats_from_chi(self, chi_redshift_pairs, figs=None):
        # TODO: Document

        best_chi = 999999999999
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

    def _set_as_rs_member(self, sources, redshift, color, bluer_color_residual_cut, redder_color_residual_cut,
                          bright_mag_cut=-999.9,  faint_mag_cut=999.9):
        """Set certain sources as red sequence members if they meet magnitude and color cuts.

        :param sources: list of sources to be tested for RS membership
        :param redshift: Redshift of the red sequence.
        :param bluer_color_residual_cut: How many magnitudes brighter than the characteristic magnitude of the RS
               sources can still be considered RS members.
        :param redder_color_residual_cut: How many magnitudes fainter than the characteristic magnitude sources will
               still be considered RS.
        :param bright_mag_cut: How many magnitudes bluer than the characteristic color a galaxy can be
        :param faint_mag_cut:
        :return: none, but sets instance attributes of sources
        """

        # First set all sources as not RS members
        for source in self.sources_list:
            source.RS_member = False

        band = color[-1]

        self._set_residuals(redshift, color)
        for source in sources:
            if (band in source.mags and self.predictions_dict[redshift].z_mag + bright_mag_cut <
                    source.mags[band] < self.predictions_dict[redshift].z_mag + faint_mag_cut and
                    bluer_color_residual_cut < source.color_residual < redder_color_residual_cut
                and source.colors[color].error <= 0.2):
                source.RS_member = True

    def _set_residuals(self, redshift, color):
        """
        Set each galaxy's color_residual instance attribute to the difference between the predicted RS color and the
        galaxy's color.

        :return: none, but instance attributes are changed in galaxy objects.
        """

        band = color[-1]

        best_z_line = self.predictions_dict[redshift].rz_line
        for source in self.sources_list:
            if band in source.mags and color in source.colors:
                if 18 < source.mags[band] < 30:  # The line used doesn't extend beyond these points.
                    idx = best_z_line.xs.index(round(source.mags[band].value, 2))
                    source.color_residual = source.colors[color].value - best_z_line.ys[idx]
                else:
                    source.color_residual = 999
            else:
                source.color_residual = 999

    def _find_location_cut(self, radius):

        # radius is in arcminutes

        # median_ra = np.median([source.ra for source in self.sources_list])
        median_ra = (max([source.ra for source in self.sources_list]) + min([source.ra for source in
                                                                             self.sources_list]))/2
        # median_decs = np.median([source.dec for source in self.sources_list])
        median_decs = (max([source.dec for source in self.sources_list]) + min([source.dec for source in
                                                                             self.sources_list]))/2

        # Override for one cluster
        # if self.name.startswith("MOO1636"):
        #     median_decs += 0.008  # best so far is 0.008
        # #     median_ra += 0.005  # best so far is 0.005
        # print median_ra, median_decs

        for source in self.sources_list:
            dist = math.sqrt((source.ra - median_ra)**2 + (source.dec - median_decs)**2)
            # if self.name.startswith("MOO2214"):
            #     # For more distant MOO2214, use 0.0 < 1.0
            #     # for less distant MOO2214, use 0.0 < 2.0
            #     if dist < 1.0/60.0:
            #         source.in_location = True
            #     else:
            #         source.in_location = False
            # if self.name.startswith("MOO1636"):
            #     # best for MOO1636: 0 < 1.3
            #     if dist < 1.3/60.0:
            #         source.in_location = True
            #     else:
            #         source.in_location = False
            if dist < radius/60.0:
                source.in_location = True
            else:
                source.in_location = False

        fig = plotting.plot_location(self)
        return fig

    def _write_rs_catalog(self):
        # TODO: Document
        # write red sequence catalog to file
        rs_catalog = open("/Users/gbbtz7/GoogleDrive/Research/Data/ClusterData/RS_catalogs/" + self.name[:-1] +
                          "_rs_members.phot.dat", "w")
        rs_catalog.write("# id    ra            dec          zmag     rmz    rmze\n")
        for source in self.sources_list:
            if source.RS_member:
                rs_catalog.write(str(source.id) + "    " + str(source.ra) + "    " + str(source.dec) + "    " + str(source.mag) +
                                 "    " + str(source.color) + "    " + str(source.color_error) + "\n")
        rs_catalog.close()
