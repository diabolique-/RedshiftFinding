import ezgal
import matplotlib.pyplot as plt

# Make a wrapper. I used C09 because it has all 3 IMFs
wrapperC09 = ezgal.wrapper(["c09_ssp_z_0.019_chab_evolved_zf_3.0_riz.model",
                            "c09_ssp_z_0.019_krou_evolved_zf_3.0_riz.model",
                            "c09_ssp_z_0.019_salp_evolved_zf_3.0_riz.model"])

#Make formation redshift, and observed redshifts
zForm = 3.0
zSeen = wrapperC09.get_zs(3.0)

# Normalize to Coma
wrapperC09.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

#Calculate apparent mags
mags = wrapperC09.get_apparent_mags(zForm, filters=['sloan_r', 'sloan_i', 'sloan_z'], zs=zSeen)
# has dimensions [models, redshift, filters]

########################################################################################################################
##              then plot r-z color vs i band mag                                                                     ##
########################################################################################################################

plt.figure(figsize=(10, 9))
#before, i need to set up line styles and labels
lineStyle = ['r-', 'g-', 'b-']
lineLabels = ["Chabrier", "Kroupa", "Salpeter"]

# put in first subplot
plt.subplot(2, 1, 1)
#need to iterate through each model...
for m in range(len(wrapperC09)):
    #Plot i band mag on x, r-z on y
    plt.plot(mags[m, :, 1], mags[m, :, 0]-mags[m, :, 2], lineStyle[m], label=lineLabels[m])

# Now adjust plot to look good
plt.legend(loc=0, prop={"size": 11})
plt.xlabel("Sloan i band apparent magnitude")
plt.ylabel("Sloan r-z Color")
plt.title("Using C09, Z=0.019, SSP, formation z=3, plotted 0<z<3", fontsize=12)
plt.suptitle("Color Magnitude Diagram for Varying IMF", fontsize=18)
plt.text(10.2, 0.8, "z=0")
plt.text(20.5, 0.1, "z=3")

#now plot differences among themselves
plt.subplot(2, 1, 2)

# plot difference from Kroupa model
# need ot iterate through each model
for m in range(len(wrapperC09)):
    # plot i band mag on x, r-z on y (but subtract Kroupa from it each time)
    # note: Kroupa index is 0
    plt.plot(mags[m, :, 1], (mags[m, :, 0]-mags[m, :, 2])-(mags[1, :, 0]-mags[1, :, 2]), lineStyle[m],
             label=lineLabels[m])

# now adjust to look good
plt.legend(loc=0, prop={"size": 11})
plt.xlabel("Sloan i band apparent magnitude")
plt.ylabel("Sloan r-z Color Difference from Kroupa")
plt.title("Differences from Kroupa IMF", fontsize=14)
plt.subplots_adjust(top=0.92, left=0.12, right=0.98, hspace=.36)
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/13-ComparingIMFWithC09iBandMag.pdf", format='pdf')

########################################################################################################################
##              Now plot everything against redshift                                                                  ##
########################################################################################################################

plt.figure(figsize=(10, 9))

# put in first subplot
plt.subplot(2, 1, 1)
#need to iterate through each model...
for m in range(len(wrapperC09)):
    #Plot i band mag on x, r-z on y
    plt.plot(zSeen, mags[m, :, 0]-mags[m, :, 2], lineStyle[m], label=lineLabels[m])

# Now adjust plot to look good
plt.legend(loc=0, prop={"size": 11})
plt.xlabel("Redshift")
plt.ylabel("Sloan r-z Color")
plt.title("Using C09, Z=0.019, SSP, formation z=3", fontsize=12)
plt.suptitle("Color vs Redshift for Varying IMF", fontsize=18)

#now plot differences among themselves
plt.subplot(2, 1, 2)

# plot difference from Kroupa model
# need ot iterate through each model
for m in range(len(wrapperC09)):
    # plot i band mag on x, r-z on y (but subtract Kroupa from it each time)
    # note: Chabrier index is 0
    plt.plot(zSeen, (mags[m, :, 0]-mags[m, :, 2])-(mags[1, :, 0]-mags[1, :, 2]), lineStyle[m], label=lineLabels[m])

# now adjust to look good
plt.legend(loc=0, prop={"size": 11})
plt.xlabel("Redshift")
plt.ylabel("Sloan r-z Color Difference from Kroupa")
plt.title("Differences from Kroupa IMF", fontsize=14)
plt.subplots_adjust(top=0.92, left=0.12, right=0.98, hspace=0.36)
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/14-ComparingIMFWithC09Redshift.pdf", format='pdf')


########################################################################################################################
##              Now plot  against age                                                                                 ##
########################################################################################################################

#need to get array of ages first
ages = wrapperC09.get_age(zForm, zSeen)  # will get list of ages from formation until present time
plt.figure(figsize=(10, 9))

# put in first subplot
plt.subplot(2, 1, 1)
#need to iterate through each model...
for m in range(len(wrapperC09)):
    #Plot i band mag on x, r-z on y
    plt.plot(ages, mags[m, :, 0]-mags[m, :, 2], lineStyle[m], label=lineLabels[m])

# Now adjust plot to look good
plt.legend(loc=0, prop={"size": 11})
plt.xlabel("Age [gyrs]")
plt.ylabel("Sloan r-z Color")
plt.title("Using C09, Z=0.019, SSP, formation z=3", fontsize=12)
plt.suptitle("Color Magnitude Diagram for Varying IMF", fontsize=18)

#now plot differences among themselves
plt.subplot(2, 1, 2)

# plot difference from Kroupa model
# need ot iterate through each model
for m in range(len(wrapperC09)):
    # plot i band mag on x, r-z on y (but subtract Kroupa from it each time)
    # note: Chabrier index is 0
    plt.plot(ages, (mags[m, :, 0] - mags[m, :, 2]) - (mags[1, :, 0] - mags[1, :, 2]), lineStyle[m], label=lineLabels[m])

# now adjust to look good
plt.legend(loc=0, prop={"size": 11})
plt.xlabel("Age [gyrs]")
plt.ylabel("Sloan r-z Color Difference from Kroupa")
plt.title("Differences from Kroupa IMF", fontsize=14)
plt.subplots_adjust(top=0.92, left=0.12, right=0.98, hspace=.36)
plt.savefig("/Users/gbbtz7/PycharmProjects/EzGal/Plots/15-ComparingIMFWithC09Age.pdf", format='pdf')