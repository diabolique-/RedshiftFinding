# find the best redshift for each cluster by fitting the models to the red sequence
from PhotoZ.files import main_functions
from PhotoZ.files import models
from PhotoZ.files import fitting
from PhotoZ.files import  plotting
import matplotlib.path as path
import matplotlib.patches as patches
import matplotlib.pyplot as plt


# need to read data in from file
images = main_functions.read_data("/Users/gbbtz7/GoogleDrive/Research/Data/madcows.specz.phot/")

# Only use r-z ones for now
images = [i for i in images if i.filters == ["r", "z"]]

# get predictions
predictions_dict = models.make_prediction_dictionary(0.01)

# make empty figure list, will append to it
figs = []

# find the best fit
for i in images:
    best_z = 9999
    best_chi = 9999  # placeholders, will be replaced
    # Set polygon that determines what points meet the cut. This will be pared down as things go along, and hopefully
    #     by the end the polygon will enclose only the red sequence
    # These initial points were found through trial and error. They tended to find the red sequence best in my sample
    top_left = [21.0, 3.5]
    bottom_left = [21.0, 1.5]
    top_right = [23.0, 3.5]
    bottom_right = [23.0, 1.5]
    codes = [1, 2, 2, 2, 79] # tell the path what to do [start, move, move, move, close path]
    vertices = [top_left, top_right, bottom_right, bottom_left, top_left]
    polygon = path.Path(vertices, codes)

    iteration = 1

    while best_chi > 1.3:
        # show polygon of cuts
        fig, ax = plotting.plot_color_mag(i, histogram=False, predictions=True, residuals=False)
        patch = patches.PathPatch(polygon, facecolor='k', alpha=0.3, lw=0)
        ax.add_patch(patch)

        for z in predictions_dict:
            chi = fitting.image_chi_square_polygon(i, predictions_dict[z].rz_line, polygon)
            if chi < best_chi:
                best_z = z
                best_chi = chi

        # Change polygon size, by adjusting color limits
        # first, get the predicted line of best redshift
        line = predictions_dict[best_z].rz_line
        l_star_mag = predictions_dict[best_z].z_mag
        # line is a list of lists with dimensions [x values, y values]

        # Plot best fit line
        ax.plot(line[0], line[1], "k-", linewidth=2)
        figs.append(fig)

        # find the index that corresponds to the magnitude of vertices
        left_idx = line[0].index(round(top_left[0], 2))
        right_idx = line[0].index(round(top_right[0], 2))

        # adjust color of points
        top_left[1] = line[1][left_idx] + 10.0 / (iteration + 9)
        top_right[1] = line[1][right_idx] + 10.0 / (iteration + 9)
        bottom_left[1] = line[1][left_idx] - 4.0 / (iteration + 9)
        bottom_right[1] = line[1][right_idx] - 4.0 / (iteration + 9)

        # # adjust magnitude of points
        # top_left[0] =  l_star_mag - ((2.0 / (iteration + 4)) + 1)
        # top_right[0] = l_star_mag + ((2.0 / (iteration + 4)) + 1)
        # bottom_left[0] = l_star_mag - ((2.0 / (iteration + 4)) + 1)
        # bottom_right[0] = l_star_mag + ((2.0 / (iteration + 4)) + 1)

        vertices = [top_left, top_right, bottom_right, bottom_left, top_left]
        polygon = path.Path(vertices, codes)




        iteration += 1


    i.photo_z = best_z
    print i.name + ", spec z = " + str(i.spec_z) + ", photo z = " + str(i.photo_z)

    # Save figures, then close them to conserve memory
    main_functions.save_as_one_pdf(figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/Cuts/" + i.name + "_z=" +
                                   str(i.spec_z) + "_pz=" + str(i.photo_z) + ".pdf")
    plt.close("all")
    del figs
    figs = []

# # save all Pdfs
# main_functions.save_as_one_pdf(figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/Cuts.pdf")

# Compare redshifts to actual ones
photo_zs, spec_zs = [], []
for i in images:
    photo_zs.append(i.photo_z)
    spec_zs.append(i.spec_z)

fig = plt.figure(figsize=(5, 5))
ax = fig.add_subplot(1, 1, 1)
ax.plot(spec_zs, photo_zs, "k.")
ax.plot([0.5, 1.5], [0.5, 1.5], "k-", lw=0.5)
ax.set_xlabel("Spectroscopic Redshift")
ax.set_ylabel("Photometric Redshift")
ax.set_title("Spectroscopic vs Photometric Redshifts")
plt.savefig("/Users/gbbtz7/GoogleDrive/Research/Plots/Spec_z_vs_photo_z.pdf", format="pdf")