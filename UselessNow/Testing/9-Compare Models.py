import ezgal
import matplotlib.pyplot as plt
import numpy as np

# make a wrapper with the models I want to compare
# I'll compare models that have Chambier IMF (or Kroupa, since it is similar), solar metallicity, SSP
wrapper = ezgal.wrapper(["bc03_ssp_z_0.02_chab_evolved_zf_3.0_ugriz.model", "c09_ssp_z_0.019_chab_evolved_zf_3.0_ugriz.model", "cb07_ssp_z_0.02_chab_evolved_zf_3.0_ugriz.model", "m05_ssp_z_0.02_krou_evolved_zf_3.0_ugriz.model", ])
# Create list of labels, will be helpful later
lineLabels = ["BC03", "C09", "CB07", "M05"]
# Set star formation redshift
zForm = 3

# Get range of redshifts
zSeen = wrapper.get_zs(2)    # only observe from 0-2

# Normalize to Coma
wrapper.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

# Calculate apparent mags in sloan filters
apparentMags = wrapper.get_apparent_mags(zForm, filters=['sloan_u', 'sloan_g', 'sloan_r', 'sloan_i', 'sloan_z'], zs=zSeen)

# mags has dimensions of [models, redshifts, filters]

# now plot
plt.figure(figsize=(15, 5))

#First Make color-mag diagram for each filter
# Make an array of different line styles for the different models
lineStyle = ['k-', 'r-', 'g-', 'b-']
# Make an array of the filters I want
filters = ['u', 'g', 'r', 'i', 'z']


#Then iterate through the filters...
for f in range(len(apparentMags[0,0,:])):
    plt.subplot(1, 5, f+1)
    # iterate through each model to plot...
    for m in range(len(wrapper)):
        plt.plot(zSeen, apparentMags[m,:,f], lineStyle[m], label=lineLabels[m])
    if f==0:
        plt.ylabel("Apparent Magnitude")
        plt.legend(loc=4)
    else:
        plt.yticks([])
    plt.ylim([10,40])
    plt.xticks([0, 0.5, 1, 1.5])
    plt.xlabel("Redshift")
    plt.title(filters[f])


# Adjust things
plt.suptitle("Comparing SPS Models Through Different Filters", fontsize=18)
plt.subplots_adjust(wspace=0, hspace=.25, top=.84, left=0.07, right=0.98)
# Then save plot
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/Colors.pdf", format='pdf')