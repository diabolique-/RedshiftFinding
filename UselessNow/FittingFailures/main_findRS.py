"""
Main function that will find the redshift of the red sequence. Recreates the plots from both Snyder 2012 and High 2010
"""
from PhotoZ.FittingFailures import RSfinding, models


# read data in. read_data returns a list of image objects
from UselessNow.NotFromImages import main_functions

images = main_functions.read_data("/Users/gbbtz7/GoogleDrive/Research/Data/madcows.specz.phot/")

# initialize empty list of figures, will fill with figures as it runs
figs = []

#  need to get model predictions
predictions = models.get_model_predictions(0.02)

# Make plots like High 2010 of number of objects in the red sequence at each redshift
for i in images:
    # Only want r-z colors to do this with for now
    if i.filters == ["r", "z"]:
        # Now need to find the best redshift
        # initialize empty lists, where we will append things later
        redshifts = []
        rs_members = []


        # Iterate through each redshift we did predictions for
        for z in predictions:
            rs_number = 0
            # make the line for the model predictions
            mags, colors, l_star_mag, l_star_color = models.make_model_lines(z, i.filters, predictions)

            # Need to round mags, so it matches the precision of the data
            mags = [round(m, 2) for m in mags]


            # Subtract this line off from all the galaxies in the image
            for gal in i.galaxy_list:
                # Throw out galaxies with colors too dim, or with bad data
                if gal.mag < (l_star_mag + 1.5) and gal.mag < 24 and gal.color_error < 1:
                    # Find the color the model predicts, given the galaxy's magnitude
                    idx = mags.index(gal.mag)
                    temp_color = gal.color - colors[idx]

                    # RS members will be within 2 sigma of the line
                    # sigma**2 = color_uncertainty**2 + intrinsic RS scatter**2
                    # Do not know anything at the moment about scatter in RS       DEFINITELY LOOK AT THIS LATER
                    sigma = gal.color_error
                    if abs(temp_color) < 2*sigma:
                        rs_number += 1

            redshifts.append(z)
            rs_members.append(rs_number)

        figs.append(RSfinding.plot_rs_histogram(redshifts,rs_members, i.name + ",  z = " + str(i.spec_z)))


main_functions.save_as_one_pdf(figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/RSHistograms.pdf")
