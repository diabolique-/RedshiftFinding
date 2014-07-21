
import ezgal
import matplotlib.pyplot as plt

# make a model using the Bruzual Charlot 03, Simple stellar population, Chabrier IMF, varying Z
BC03008 = ezgal.model("bc03_ssp_z_0.008_chab.model")
BC0302 = ezgal.model("bc03_ssp_z_0.02_chab.model")
BC0305 = ezgal.model("bc03_ssp_z_0.05_chab.model")

# set formation redshift
zForm = 3

# set the model normalization to Dai et al 2009 (ApJ, 697, 506)
BC03008.set_normalization('ch1', 0.24, -25.06, vega=True)
BC0302.set_normalization('ch1', 0.24, -25.06, vega=True)
BC0305.set_normalization('ch1', 0.24, -25.06, vega=True)


#Get array of redshifts so we can plot using that
zSeen = BC03008.get_zs(1.5)
# zSeen will be the same for all the models, since it doesn't depend on the specifics

#Get 3 bands apparent mag for all Z
i008 = BC03008.get_apparent_mags(zForm, filters = "sloan_i", zs = zSeen)
r008 = BC03008.get_apparent_mags(zForm, filters = "sloan_r", zs = zSeen)
z008 = BC03008.get_apparent_mags(zForm, filters = "sloan_z", zs = zSeen)

i02 = BC0302.get_apparent_mags(zForm, filters = "sloan_i", zs = zSeen)
r02 = BC0302.get_apparent_mags(zForm, filters = "sloan_r", zs = zSeen)
z02 = BC0302.get_apparent_mags(zForm, filters = "sloan_z", zs = zSeen)

i05 = BC0305.get_apparent_mags(zForm, filters = "sloan_i", zs = zSeen)
r05 = BC0305.get_apparent_mags(zForm, filters = "sloan_r", zs = zSeen)
z05 = BC0305.get_apparent_mags(zForm, filters = "sloan_z", zs = zSeen)




#attempt a color magnitude plot
plt.plot(i008, (r008-z008), "b-", label = "Z = 0.008")
plt.plot(i02, (r02-z02), "g-", label = "Z = 0.02")
plt.plot(i05, (r05-z05), "r-", label = "Z = 0.05")
plt.xlabel("i band mag")
plt.ylabel("r-z color")
plt.suptitle("Color Magnitude of varying Metallicity(Z)", fontsize=18)
plt.title("Using BC03, SSP, Chabrier IMF", fontsize=12)
plt.legend(loc = 0)




plt.show()
