# find the best redshift for each cluster by fitting the models to the red sequence
from PhotoZ.files import main_functions
from PhotoZ.files import models
from PhotoZ.files import fitting
import matplotlib.pyplot as plt


# need to read data in from file
images = main_functions.read_data("/Users/gbbtz7/GoogleDrive/Research/Data/madcows.specz.phot/")

# Only use r-z ones for now
images = [i for i in images if i.filters == ["r", "z"]]

# get predictions
predictions_dict = models.make_prediction_dictionary(0.01)

# find the best fit
for i in images:
    best_z = 9999
    best_chi = 9999  # placeholders, will be replaced
    # Set cut limits, will be pared down as things go along
    min_color = 1.5
    max_color = 5.0
    min_mag = 20.0
    max_mag = 23.0
    while best_chi > 2:
        for z in predictions_dict:
            chi = fitting.image_chi_square_polygon(i, predictions_dict[z].rz_line, min_mag, max_mag, min_color, max_color)
            if chi < best_chi:
                best_z = z
                best_chi = chi

        # make limits tighter, depending on how good the fit is so far
        min_color += (2.0 / 10.0) * ((predictions_dict[best_z].r_mag - predictions_dict[best_z].z_mag) - min_color)
        max_color -= (1.0 / 10.0) * (max_color - (predictions_dict[best_z].r_mag - predictions_dict[best_z].z_mag))
        # min_mag += (1 / best_chi) * (predictions_dict[best_z].z_mag - min_mag)
        # max_mag -= (1 / best_chi) * (max_color - predictions_dict[best_z].z_mag)

    i.photo_z = best_z
    print i.name + ", spec z = " + str(i.spec_z) + ", photo z = " + str(best_z) + ", chi = " + str(best_chi) + \
        ", min color = " + str(min_color) + ", max color = " + str(max_color)

photo_zs, spec_zs = [], []
for i in images:
    photo_zs.append(i.photo_z)
    spec_zs.append(i.spec_z)

plt.scatter(spec_zs, photo_zs)
plt.plot([0, 1.5], [0, 1.5])
plt.show()