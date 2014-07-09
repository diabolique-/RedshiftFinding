# find the best redshift for each cluster by fitting the models to the red sequence
from Project.files import main_functions
from Project.files import fitting
from Project.files import plotting
import matplotlib.pyplot as plt

# need to read data in from file
images = main_functions.read_image_objects()

# Only use r-z ones for now
images = [i for i in images if i.filters == ["r", "z"]]

# get predictions
predictions_dict_01 = main_functions.make_prediction_dictionary(0.01)
predictions_dict_02 = main_functions.make_prediction_dictionary(0.02)

# Make empty list for plots, will append later
residual_plots = []
cmd_figs = []

# find the best fit
for i in images:
    # Plot initial cmd, append to list
    fig, ax = plotting.plot_color_mag(i, predictions=True)
    cmd_figs.append(fig)
    # call the function to find the best red sequence. It returns a list of figures
    temp_cmds = fitting.find_rs_redshift_color_cuts(i, predictions_dict_01, predictions_dict_02, plot_cuts=True)
    # Put these figures one by one into a list, so it can be saved later
    for cmd in temp_cmds:
        cmd_figs.append(cmd)

    # Write results to the file
    print i.name + ", spec z = " + str(i.spec_z) + ", photo z = " + str(i.photo_z)

# # Plot residuals colors
# for j in images:
#     residual_plots.append(plotting.plot_residuals(j))

# save all  PDFs, if the program made figures for them
if residual_plots:
    main_functions.save_as_one_pdf(residual_plots, "/Users/gbbtz7/GoogleDrive/Research/Plots/Residuals.pdf")
if cmd_figs:
    main_functions.save_as_one_pdf(cmd_figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/Cuts.pdf")

# Plot redshift comparison
plotting.plot_z_comparison(images, "/Users/gbbtz7/GoogleDrive/Research/Plots/", "Spec_z_vs_photo_z")

print "\nDone plotting. All that's left is closing figures."

# close all figures
plt.close("all")