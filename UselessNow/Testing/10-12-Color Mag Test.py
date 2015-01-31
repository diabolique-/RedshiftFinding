import ezgal
import matplotlib.pyplot as plt
import matplotlib.collections as col

# Make a wrapper with the models
#3 IMF types, leave one uncommented
wrapper = ezgal.wrapper(["bc03_ssp_z_0.02_chab_evolved_zf_3.0_ugriz.model", "c09_ssp_z_0.019_chab_evolved_zf_3.0_ugriz.model", "cb07_ssp_z_0.02_chab_evolved_zf_3.0_ugriz.model"])
# Models are pre-evolved, so code will run faster
#wrapper = ezgal.wrapper(["bc03_ssp_z_0.02_salp.model", "c09_ssp_z_0.019_salp.model", "cb07_ssp_z_0.02_salp.model", "m05_ssp_z_0.02_salp.model", "p2_ssp_z_0.02_salp.model"])
#wrapper = ezgal.wrapper(["basti_ssp_n_0.4_z_0.0198_krou.model", "c09_ssp_z_0.019_krou.model", "m05_ssp_z_0.02_krou.model"])

# Set formation redshift, and seen redshifts
zForm = 3
zSeen = wrapper.get_zs(1.8)

# Normalize to Coma
wrapper.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

#Calculate apparent mags in r, i, z colors
apparentMags = wrapper.get_apparent_mags(zForm, filters=['sloan_r', 'sloan_i', 'sloan_z'], zs=zSeen)
# has dimensions of [model, redshift, filter]

# Plot r-z color vs i magnitude
plt.figure(figsize=(9,5))
#need to set colors and labels for models
lineStyle = ['b-', 'r-', 'g-']          # rename as needed
lineLabels = ["BC03", "C09", "CB07"]    # rename as needed
# Need to iterate through all models
for m in range(len(apparentMags)):
    plt.plot(apparentMags[m,:,1], apparentMags[m,:,0]-apparentMags[m,:,2], lineStyle[m], label=lineLabels[m])
plt.suptitle("Sloan r-z Color vs i Band Magnitude", fontsize=18)
plt.title("Using Z=0.02, simple stellar population, Chabrier IMF, formation z=3", fontsize=12)
plt.xlabel("Apparent i band Magnitude")
plt.ylabel("r-z Color")
plt.legend(loc=0)
plt.subplots_adjust(left=0.07, right=0.95, top=0.86)
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/10-ColorMagChabrier.pdf", format='pdf')
