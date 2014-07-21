import ezgal
import matplotlib.pyplot as plt

# Make a wrapper with everything the same except metallicity
wrapper = ezgal.wrapper(["bc03_ssp_z_0.008_chab_evolved_zf_3.0_ugriz.model",
                         "bc03_ssp_z_0.02_chab_evolved_zf_3.0_ugriz.model",
                         "bc03_ssp_z_0.05_chab_evolved_zf_3.0_ugriz.model"])

# Set labels and line stlyes for later graphing
lineLabels = ["Z=0.008", "Z=0.02", "Z=0.05"]
lineStyles = ["b-", "g-", "r-"]

# set formation redshift, and viewing redshifts
zForm = 3.0
zSeen = wrapper.get_zs(zForm)

# Normalize to Coma
wrapper.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

# Get apparent mags
mags = wrapper.get_apparent_mags(zForm, filters=["sloan_u", "sloan_g", "sloan_r", "sloan_i", "sloan_z"], zs=zSeen)
# has dimensions of [models, redshifts, filters]

#plot r-z color vs redshift
#make a figure
plt.figure(figsize=(8, 6))

#need to iterate through all models to plot
for m in range(len(wrapper)):
    plt.plot(zSeen, mags[m, :, 2]-mags[m, :, 4], lineStyles[m], label=lineLabels[m])

# set labels and whatnot
plt.suptitle("r-z Color vs Redshift for Varying Metallicity", fontsize=17)
plt.title("Using BC03, SSP, Chabrier IMF, formation z=3.0", fontsize=11)
plt.xlabel("Redshift")
plt.ylabel("Sloan r-z Color")
plt.legend(loc=0)
plt.show()
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/18-ComparingZ-Colorz.pdf", format="pdf")