from PhotoZ.files import main_functions
from PhotoZ.files import plotting


# need to read data in from file
clusters = main_functions.read_cluster_objects()

# Only use ones with r-z data for now
clusters = [c for c in clusters if c.filters == ["r", "z"]]


# Make empty list for plots, will append later
residual_plots = []
cmd_figs = []

# find the best fit
for c in clusters:
#     if  c.name.startswith("MOOOO1636"):
    if True:
        # c.fit_z()  # No plot
        c.fit_z(cmd_figs)  # Plots
        # WARNING: If plotting is used for both the beginning, end, and the fitting procedure, it would be wise to reduce
        # the iterations in the bootstrapping (or change the _find_rs_redshift call in _bootstrap) or you will literally
        # get >1000 plots, and it will slow the computer to a halt.

        # Print results, to see progress.
        print c.name + ", spec z = " + str(c.spec_z) + ", photo z = " + str(c.photo_z)

# Save pdfs
if cmd_figs:
    main_functions.save_as_one_pdf(cmd_figs, "/Users/gbbtz7/GoogleDrive/Research/Plots/Cuts.pdf")

# Plot redshift comparison
plotting.plot_z_comparison(clusters, "/Users/gbbtz7/GoogleDrive/Research/Plots/", "Spec_z_vs_photo_z")