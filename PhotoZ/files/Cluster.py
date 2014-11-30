from PhotoZ.files import plotting
from PhotoZ.files import functions
from PhotoZ.files import predictions
import math
from PhotoZ.files import global_paths


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
            # compare the name against a known list of redshifts, to see if it is known.
            known_redshifts = {"MOO0012+1602": "0.94", "MOO0024+3303": "1.11", "MOO0125+1344": "1.12",
             "MOO0130+0922": "1.15", "MOO0133-1057": "0.96", "MOO0212-1813": "1.09", "MOO0224-0620": "0.81",
             "MOO0245+2018": "0.76", "MOO0319-0025": "1.19", "MOO1155+3901": "1.01", "MOO1210+3154": "1.05",
             "MOO1319+5519": "0.94", "MOO1335+3004": "0.98", "MOO1514+1346": "1.06", "MOO1625+2629": "1.20",
             "MOO2205-0917": "0.93", "MOO2320-0620": "0.92", "MOO2348+0846": "0.89", "MOO2355+1030": "1.27"}
            if "catalog" in self.name: # To handle duplicate clusters that I have named with catalog
                self.spec_z = known_redshifts[self.name.split()[0]]
            elif self.name in known_redshifts: # will handle normal clusters
                self.spec_z = known_redshifts[self.name]
            else:
                self.spec_z = None

        self.sources_list = sources_list

        self.r_data = False
        self.i_data = False
        self.z_data = False
        self.ch1_data = False
        self.ch2_data = False
        self.rs_z = dict()
        self.upper_photo_z_error = dict()
        self.lower_photo_z_error = dict()

    def __repr__(self):  # how the object appears when printed
        return self.name

    def calculate_color(self):
        for source in self.sources_list:
            source.calculate_color()




    ######################################

    # Documentation needed below this line

    #######################################


    def fit_z(self, color, plot_figures=False):
        """Find the redshift of the cluster by matching its red sequence to the models.
        Basically works as the main function for this process. Other functions are called to do the dirty work.

        :param color: str with the color that the fitting procedure will be done with. Should be in the format
        "band1-band2" (like "r-z")
        :param plot_figures: To plot figures, pass in a list that the figures will be appended to.
                             If no plotting is desired, leave the parameter blank (i.e. pass nothing in).
        :return: None, but the instance variables for photometric redshift and photo z error are set inside.
        """

        # initialize list to append figures to
        figures_list = []
        # Find a good starting redshift to base the rest of the work on, and set RS membership

        if "z" not in self.name:
            if self.name == "MOO0037+3306" or self.name == "MOO0105+1323":
                pass
                # self._find_xy_cut(750)  # TODO: write better cut function
            else:
                self._find_location_cut(1.5)  # To do no plotting



        initial_z = self._find_initial_redshift(color, plot_bar=plot_figures, figs_list=figures_list)

        # set red sequence cut based on the initial redshift
        self._set_as_rs_member(self.sources_list, initial_z, color, -0.1, 0.1, -1.2, 0.5)

        # If plot_figures is a list, plot and append. If nothing was passed in, this will not trigger.
        if plot_figures:
            # Plot with predictions
            figures_list.append(plotting.plot_color_mag(self, color, band=color[-1], predictions=True,
                                                        distinguish_red_sequence=False))
            # Plot the initial cut with RS based on the initial cut
            figures_list.append(plotting.plot_fitting_procedure(self, color, color[-1], initial_z, other_info="Initial "
                                                                "Fitting", color_red_sequence=True))
            pass  # So when I comment all the plots out it still runs

        bluer_color_cut = [-0.25, -0.225, -0.20]
        # if self.name.startswith("MOO1636"):
        #     bluer_color_cut = [-0.2, -0.2, -0.2]  # Override to avoid "foregrounds." Not sure if actually foregrounds
        redder_color_cut = [0.4, 0.3, 0.2]
        brighter_mag_cut = -1.4
        dimmer_mag_cut = 0.6



        self._set_as_rs_member(self.sources_list, initial_z, color, bluer_color_cut[0], redder_color_cut[0],
                               brighter_mag_cut, dimmer_mag_cut)

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
            figures_list.append(plotting.plot_fitting_procedure(self, color, color[-1], best_z, other_info="Cut " + str(
                i+1)))

            chi_redshift_list = self._fit_redshift_to_sample(sample, color, color[-1])

            best_z, z_lower_error, z_upper_error = self._get_stats_from_chi(chi_redshift_list)




        # Set cluster attributes, now that the process is complete
        self.rs_z[color] = best_z
        self.upper_photo_z_error[color] = z_upper_error
        self.lower_photo_z_error[color] = z_lower_error

        # Make final RS cut, which will be slightly larger than the cut used to identify the RS
        self._set_as_rs_member(self.sources_list, self.rs_z[
            color], color, -0.3, 0.6, -1.4,
                                1.0)
        # self._set_as_rs_member([source for source in self.sources_list if source.in_location], self.rs_z, color, -0.3, 0.6,
        #                        -1.2, 1.0)
        # Override for lower redshift struture, since there is a higher structure that gets in the way
        # if self.name.startswith("MOO2214"):
        #     self._set_as_rs_member(self.sources_list, self.rs_z[color], color, -0.2, 0.2, -1.2, 0.8)
        # if self.name.startswith("MOO1636"):
        #     self._set_as_rs_member(self.sources_list, self.rs_z[color], color, -0.3, 0.6, -1.6, 1.0)


        # Plot final redshift on CMD
        if plot_figures:
            figures_list.append(plotting.plot_fitting_procedure(self, color, color[-1], self.rs_z[color],
                                                                "Final Redshift", color_red_sequence=True))
            figures_list.append(plotting.plot_location(self))
            pass # again so I can comment out plots if I want

        self._write_rs_catalog()

        # Save the plots
        functions.save_as_one_pdf(figures_list, global_paths.plots + str(self.name) + ".pdf")


        print self, self.rs_z[color]





    def _find_initial_redshift(self, color, plot_bar=False, figs_list=None):
        """Find a good redshift for the cluster, based on the highest number of galaxies near a predicted RS line.

        Iterates through all redshifts, and counts the number of galaxies within 0.1 color of the model line. Then
        the redshift that has the highest number of galaxies (including some contributions from neighboring
        redshifts) is the redshift selected. This redshift is not necessarily the best fit, just a good starting
        place for more sophisticated fitting.

        :param plot_bar: Whether or not to make a bar graph showing the number of galaxies near each redshift.
        :param figs_list: the list the figures will be appended to, if they are plotted
        :return: best fitting redshift.

        """
        # TODO: I don't know if I really need to do this. I could just do fitting without this starting poitn
        # Initialize empty lists, will append as we go
        galaxies_list = []
        z_list = []

        # Iterate through each redshift we have predictions for
        for z in sorted(self.predictions_dict.iterkeys()):  # need to be sorted, since we will be including neighbors
            rs_members = 0
            self._set_as_rs_member(self.sources_list, z, color, -0.1, 0.1, -1.2, 0.5)  # 3rd spot could be -2.0
            for source in self.sources_list:
                if source.RS_member and source.in_location:
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
            figs_list.append(plotting.plot_initial_redshift_finding(self, z_list, galaxies_list, best_z))

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

        # If the limits aren't replaced, set the limits to be nearly at the point.
        if left_limit == 1.6:
            left_limit = float(best_z) - 0.005
        if right_limit == 0.4:
            right_limit = float(best_z) + 0.005

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


    def _find_xy_cut(self, radius):
        middle_x = (max([source.ra for source in self.sources_list]) + min([source.ra for source in
                                                                             self.sources_list]))/2
        middle_y = (max([source.dec for source in self.sources_list]) + min([source.dec for source in
                                                                             self.sources_list]))/2

        for source in self.sources_list:
            dist = math.sqrt((source.ra - middle_x)**2 + (source.dec - middle_y)**2)

            if dist < radius:
                source.in_location = True
            else:
                source.in_location = False

    def _write_rs_catalog(self):
        # TODO: document
        # open the file for writing
        rs_catalog = open(global_paths.rs_catalogs + self.name + "_rs_members.cat", "w")

        # create the labels at the top (with fixed widths)
        rs_catalog.write("{:13s} {:13s}".format("#ra", "dec"))
        # Only include labels for bands if the cluster actually has data in that band
        if self.r_data:
            rs_catalog.write("{:10s} {:8s}".format("r_mag", "r_err"))
        if self.z_data:
            rs_catalog.write("{:10s} {:8s}".format("z_mag", "z_err"))
        rs_catalog.write("rs_member\n")

        # Iterate through the sources in the cluster, and put their data in the file too.
        for source in self.sources_list:
            rs_catalog.write("{:13s} {:13s}".format(str(source.ra), str(source.dec)))
            if self.r_data:
                try:
                    rs_catalog.write("{:10s} {:8s}".format(str(source.mags["r"].value), str(round(source.mags[
                                                                                                "r"].error, 4))))
                except KeyError:
                    rs_catalog.write("{:10s} {:8s}".format(" ", " "))
            if self.z_data:
                try:
                    rs_catalog.write("{:10s} {:8s}".format(str(source.mags["z"].value), str(round(source.mags[
                                                                                                "z"].error, 4))))
                except KeyError:
                    rs_catalog.write("{:10s} {:8s}".format(" ", " "))
            if source.RS_member:
                rs_catalog.write("1")
            else:
                rs_catalog.write("0")
            rs_catalog.write("\n")
        rs_catalog.close()
