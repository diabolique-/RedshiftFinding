# contains function used for fitting the redshfit to the cluster
from PhotoZ.files import plotting
from PhotoZ.files import main_functions
import matplotlib.path as path
import matplotlib.patches as patches
import matplotlib.pyplot as plt




def find_RS_redshift_color_cuts(image, predictions, plot_cuts=False):

    # Set placeholders that will be replaced as the chi fitting runs
    best_chi_sq = 999
    best_z = 1

    # Initial cuts will be centered on the prediction for redshift = 1. This will allow for quicker fitting. If the
    # first redshift is the fit of the whole image, it is often very low, and this make it hard to fit red sequences
    # at high redshift (and therefore color). This approach eliminates that trouble.

    iteration = 1.0  # set a counter that will be used in the loop
    figs = []  # initialize empty list, will be filled if things are plotted

    # Want to find a fit that is decent
    while best_chi_sq > 1.3:

        # build the polygon that determines the color cuts
        # A polygon is used because the slope of the red sequence is non zero. Horizontal color cuts would not make for
        # a good fit.
        # The polygon will have set magnitude limits, and color limits above and below the best prediction so far. This
        # will make the code gradually get closer to the correct red sequence.

        # To do this, first we need to get the predicted line of best redshift fit so far
        line = predictions[best_z].rz_line
        # This line will be a list of lists with dimensions [x values, y values] (for the line)

        # the left and right magnitude cuts will be at 21.0 and 23.0. We need to find the colors of the prediction that
        # match those values
        left_idx = line[0].index(21.0)
        right_idx = line[0].index(23.0)

        # Now set the vertces of the cuts polygon using the color of the best fit line
        # As the iterations increase, the color cuts will get smaller (closer to the best fit)
        top_left = [21.0, line[1][left_idx] + (10.0 / (iteration + 9))]
        top_right = [23.0, line[1][right_idx] + (10.0 / (iteration + 9))]
        bottom_left = [21.0, line[1][left_idx] - (4.0 / (iteration + 5))]
        bottom_right = [23.0, line[1][right_idx] - (4.0 / (iteration + 5))]
        # I used 10 or 4 / (iteration + 9 or + 5) so that the cuts were smoother. I didn't want for it to go from +1
        # to +1/2 to +1/4. That would be too drastic, and may miss the red sequence entirely

        # Turn these points into a polygon
        codes = [1, 2, 2, 2, 79] # tell the path what to do [start, move, move, move, close path]
        vertices = [top_left, top_right, bottom_right, bottom_left, top_left]
        polygon = path.Path(vertices, codes)

        # Plot the polygon and best fit line
        if plot_cuts:

            fig, ax = plotting.plot_color_mag(image, predictions=True)
            patch = patches.PathPatch(polygon, facecolor='k', alpha=0.3, lw=0)
            ax.add_patch(patch)
            ax.plot(line[0], line[1], "k-", linewidth=2)
            ax.set_title(image.name + ", spec z = " + str(image.spec_z) + ", photo z = " + str(best_z))
            figs.append(fig)

        # Now find the new best fit line for the points in the polygon
        for z in sorted(predictions.iterkeys()):
            chi_sq = image_chi_square(image, predictions[z].rz_line, polygon)
            if chi_sq < best_chi_sq:
                best_chi_sq = chi_sq
                best_z = z

        # Increment counter
        iteration += 1.0

    # Set the instance attribute
    image.photo_z = best_z

    # Set the residuals for all the galaxies using the best fit model line
    for gal in image.galaxy_list:
        if 19 < gal.mag < 27:  # Only certain range I have good data for
            # Find the location of the correspoinding color the model predicts at the galaxies magnitude
            idx = predictions[best_z].rz_line[0].index(gal.mag)
            gal.color_residual = gal.color - predictions[best_z].rz_line[1][idx]

    if plot_cuts:
        # Save figures, then close them to conserve memory
        main_functions.save_as_one_pdf(figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/Cuts/" + image.name + "_z=" +
                                   str(image.spec_z) + ".pdf")
        plt.close("all")



def image_chi_square(image, model_line, polygon):
    # return the reduced chi square value for the fit of the given line on the given image
    chi_sq = 0
    good_galaxies = 0
    for gal in image.galaxy_list:

        # Some galaxies are clear outliers, or have bad data
        # only use points that are inside the polygon I want
        if 0.001 < gal.color_error < 10 and polygon.contains_point([gal.mag, gal.color]):
            good_galaxies += 1
            # find color model predicts for the galaxy at the given magnitude
            idx = model_line[0].index(gal.mag)
            chi_sq += ((model_line[1][idx] - gal.color) / gal.color_error)**2

    return chi_sq / good_galaxies
