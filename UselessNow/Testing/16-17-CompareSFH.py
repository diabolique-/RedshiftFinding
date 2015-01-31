import ezgal
import matplotlib.pyplot as plt

#load pre-evolved models into a wrapper
wrapper = ezgal.wrapper(["bc03_ssp_z_0.02_chab_evolved_zf_3.0_ugriz.model",
                         "bc03_burst_0.1_z_0.02_chab_evolved_zf_3.0_ugriz.model",
                         "bc03_exp_0.1_z_0.02_chab_evolved_zf_3.0_ugriz.model",
                         "bc03_exp_1.0_z_0.02_chab_evolved_zf_3.0_ugriz.model",
                         "bc03_const_1.0_tV_1.0_z_0.02_chab_evolved_zf_3.0_ugriz.model"])

# Set some things up for easier plotting later
wrapperLabels = ["SSP", "0.1 gyr Burst", "Exponential, Tau = 0.1 gyr", "Exponential, Tau = 1.0 gyr", "Constant"]
lineStyles = ["k-", "r-", "g-", "b-", "c-"]

# set formation redshift, and viewing redshifts
zForm = 3.0
zSeen = wrapper.get_zs(zForm)
zSeen2 = wrapper.get_zs(2.0)

# Normalize to Coma
wrapper.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

#find apparent mags in u, g, r, i, z
mags = wrapper.get_apparent_mags(zForm, filters=["sloan_u", "sloan_g", "sloan_r", "sloan_i", "sloan_z"], zs=zSeen)
mags2 = wrapper.get_apparent_mags(zForm, filters=["sloan_u", "sloan_g", "sloan_r", "sloan_i", "sloan_z"], zs=zSeen2)
# has dimensions of [models, redshift, filter]

#get ages, for later plotting
ages = wrapper.get_age(zForm, zSeen)

###############################################################################
##     Plot Color Magnitude Diagram
###############################################################################

# create the figure
plt.figure(figsize=(10, 7))

# Need to iterate through all models to plot them
for m in range(len(wrapper)):
    # plot i on x, r-z on y, use formatting from above
    plt.plot(mags2[m, :, 3], mags2[m, :, 2]-mags2[m, :, 4], lineStyles[m], label=wrapperLabels[m])

# Add labels and formatting
plt.xlabel("Sloan i band magnitude")
plt.ylabel("Sloan r-z color")
plt.title("Using BC03, Z=0.02, Chabrier IMF, formation z=3.0, plotted 0<z<2.0", fontsize=12)
plt.suptitle("Color Magnitude Diagram for Different Star Formation Histories", fontsize=18)
plt.legend(loc=0, prop={"size": 11})
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/16-ComparingSFH-ColorMag.pdf", format='pdf')


###############################################################################
##     Plot color vs Redshift
###############################################################################

#create a figure
plt.figure(figsize=(10, 7))

# need to iterate through all models to plot them
for m in range(len(wrapper)):
    # x:redshift, y:r-z
    plt.plot(zSeen, mags[m, :, 2]-mags[m, :, 4], lineStyles[m], label=wrapperLabels[m])

# add labels and formatting
plt.xlabel("Redshift")
plt.ylabel("Sloan r-z color")
plt.title("Using BC03, Z=0.02, Chabrier IMF, formation z=3.0", fontsize=12)
plt.suptitle("Color vs Redshift for Different Star Formation Histories", fontsize=18)
plt.legend(loc=0, prop={"size": 11})
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/17-ComparingSFH-ColorZ.pdf", format='pdf')