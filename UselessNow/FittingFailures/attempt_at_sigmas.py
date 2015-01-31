import matplotlib.pyplot as plt

from PhotoZ.files import main_functions
from UselessNow.NotFromImages import plotting


def find_redshift_sigma_clipping(image, predictions, plot_process=True):
    # Initialize empty list of figures that will be appended to
    figs = []


    # Make a starting place
    best_z = 1.0
    MAX_ITERATIONS = 10
    # Do fitting and sigma clipping a certain number of times before stopping
    for i in range(MAX_ITERATIONS):

        # Calculate residuals for all galaxies, so we can assign RS membership later
        for gal in image.galaxy_list:
            # Only use good data
            if not gal.bad_data:
                idx = predictions[best_z].rz_line[0].index(gal.mag)
                gal.color_residual = abs(predictions[best_z].rz_line[1][idx] - gal.color)

        # Now Cut out galaxies that are more then 3 standard deviations from the best fit line
        for gal in image.galaxy_list:
            if gal.color_error > 0:
                if (gal.color_residual / gal.color_error) < (MAX_ITERATIONS - i):
                    gal.RS_member = True
                else:
                    gal.RS_member = False

        # Plot the CMD, where the RS members will be distinguished
        if plot_process:
            fig, ax = plotting.plot_color_mag(image, histogram=False, predictions=True, residuals=False)
            ax.set_title(image.name + ", spec z = " + str(image.spec_z) + ", photo z = " + str(best_z))
            figs.append(fig)

        # Find the new best fit redshift
        best_chi_sq = 999
        for z in predictions:
            chi_sq = weighted_psuedo_chi_squared(image, predictions[z].rz_line)
            if chi_sq < best_chi_sq:
                best_chi_sq = chi_sq
                best_z = z


    # Plot the final cut
    if plot_process:
        fig, ax = plotting.plot_color_mag(image, histogram=False, predictions=True, residuals=False)
        ax.set_title(image.name + ", spec z = " + str(image.spec_z) + ", photo z = " + "none")
        figs.append(fig)


    # Set the instance attribute
    image.photo_z = best_z

    # Save figures, then close them to conserve memory
    main_functions.save_as_one_pdf(figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/Cuts/" + image.name + "_z=" +
                                   str(image.spec_z) + ".pdf")
    plt.close("all")



def image_chi_square(image, model_line):
    chi_sq = 0
    good_galaxies = 0
    for gal in image.galaxy_list:

        # Only use red sequence members
        if gal.RS_member and not gal.bad_data:
            good_galaxies += 1
            # find color model predicts for the galaxy at the given magnitude
            idx = model_line[0].index(gal.mag)
            gal.color_residual = model_line[1][idx] - gal.color
            chi_sq += (gal.color_residual / gal.color_error)**2

    return chi_sq / good_galaxies  # returns reduced chi squared

def weighted_psuedo_chi_squared(image, model_line):
    chi_sq = 0
    good_galaxies = 0
    for gal in image.galaxy_list:

        # Only use red sequence members
        if gal.RS_member and not gal.bad_data:
            good_galaxies += 1
            # find color model predicts for the galaxy at the given magnitude
            idx = model_line[0].index(gal.mag)
            gal.color_residual = model_line[1][idx] - gal.color
            # calculate chi squared, but weight magnitudes (brighter is more important)
            chi_sq += (gal.color_residual / gal.color_error)**2 / (gal.mag - 20)

    return chi_sq / good_galaxies  # returns reduced chi squared