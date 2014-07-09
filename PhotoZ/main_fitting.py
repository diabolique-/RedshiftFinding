from PhotoZ.files import main_functions
from PhotoZ.files import fitting
from PhotoZ.files import plotting


# need to read data in from file
images = main_functions.read_image_objects()

# Only use r-z ones for now
images = [i for i in images if i.filters == ["r", "z"]]


# get predictions
predictions_dict = main_functions.make_prediction_dictionary(0.01)


# Make empty list for plots, will append later
residual_plots = []
cmd_figs = []

# find the best fit
for i in images:
    cmd_figs.append(fitting.fit_z(i, predictions_dict))

    # Write results to the file
    print i.name + ", spec z = " + str(i.spec_z) + ", photo z = " + str(i.photo_z)


if cmd_figs:
    main_functions.save_as_one_pdf(cmd_figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/Cuts.pdf")

# Plot redshift comparison
plotting.plot_z_comparison(images, "/Users/gbbtz7/GoogleDrive/Research/Plots/", "Spec_z_vs_photo_z")