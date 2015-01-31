import ezgal
import matplotlib.pyplot as plt

# make a wrapper object with the CB03 model, solar metallicity, Chabrier IMF, and varying SFH
wrapper = ezgal.wrapper(["bc03_burst_0.1_z_0.02_chab.model", "bc03_exp_0.1_z_0.02_chab.model", "bc03_exp_1.0_z_0.02_chab.model", "bc03_ssp_z_0.02_chab.model"])

# normalize the models to coma
wrapper.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

# set formation redshift
zForm = 3.0

# get array of redshifts
zSeen = wrapper.get_zs(1.5)

# fetch absolute mag vs redshift for all models in Sloan i
mags = wrapper.get_apparent_mags( zForm, filters=['sloan_r', 'sloan_i', 'sloan_z'], zs=zSeen )

# make line style for each model
lineStyle = ['k-', 'r-', 'c-', 'b-']
# and make labels
labels = ["0.1 Gyr burst", "exponential, tau = 0.1 Gyr", "exponential, tau = 1.0 Gyr", "simple stellar population"]

# now plot
# do r-z color vs i band color
#iterate through each model
for i in range(len( wrapper )):
    # the mags datacube has dimensions of [model, redshifts, filters]
	plt.plot( mags[i,:,1], mags[i,:,0]-mags[i,:,2], lineStyle[i], label=labels[i] )
plt.xlabel( 'Sloan i band mag' )
plt.ylabel( 'Sloan r-z color' )
plt.suptitle("Color Magnitude for Varying Star Formation Histories", fontsize=18)
plt.title("Using BC03, solar metallicity, Chabrier IMF")
plt.legend(loc=0)
#plt.savefig("test.pdf", format='pdf')
plt.show()