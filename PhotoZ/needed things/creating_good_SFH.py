import ezgal
import numpy as np
import matplotlib.pyplot as plt

# Make models
model = ezgal.ezgal("c09_ssp_z_0.019_chab.model")
exp05 = model.make_exponential(0.05)
exp10 = model.make_exponential(0.10)
exp20 = model.make_exponential(0.20)
exp30 = model.make_exponential(0.30)
exp35 = model.make_exponential(0.35)
exp40 = model.make_exponential(0.40)



wrapper = ezgal.wrapper([exp05, exp10, exp20, exp30, exp35, exp40])

# Set normalization to Coma
wrapper.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

zform = 3.0
zseen = np.arange(0.1, 1.9, 0.01)

mags = wrapper.get_apparent_mags(zf=zform, zs=zseen, filters=["sloan_u", "sloan_g","sloan_r","sloan_i", "sloan_z",
                                                              "ch1", "ch2"])
# has elements of [models, redshifts, filters]

# save the models
wrapper[0].save_model(
    "/Library/Python/2.7/site-packages/ezgal/data/models/c09_exp_0.05_z_0.019_chab_evolved_zf_3.0_ugrizch1ch2.model")
wrapper[1].save_model(
    "/Library/Python/2.7/site-packages/ezgal/data/models/c09_exp_0.1_z_0.019_chab_evolved_zf_3.0_ugrizch1ch2.model")
wrapper[2].save_model(
    "/Library/Python/2.7/site-packages/ezgal/data/models/c09_exp_0.2_z_0.019_chab_evolved_zf_3.0_ugrizch1ch2.model")
wrapper[3].save_model(
    "/Library/Python/2.7/site-packages/ezgal/data/models/c09_exp_0.3_z_0.019_chab_evolved_zf_3.0_ugrizch1ch2.model")
wrapper[4].save_model(
    "/Library/Python/2.7/site-packages/ezgal/data/models/c09_exp_0.35_z_0.019_chab_evolved_zf_3.0_ugrizch1ch2.model")
wrapper[5].save_model(
    "/Library/Python/2.7/site-packages/ezgal/data/models/c09_exp_0.4_z_0.019_chab_evolved_zf_3.0_ugrizch1ch2.model")


# Plot r-z color vs redshift
labels = ["tau=0.05 Gyr", "tau=0.1 Gyr", "tau=0.2 Gyr", "tau=0.3 Gyr", "tau=0.35 Gyr", "tau=0.4 Gyr", "tau=1.0 Gyr"]
styles = ["k-", "r-", "g-", "b-", "c-", "m-", "y-"]
fig = plt.figure(figsize=(9, 6))
for m in range(len(wrapper)):
    plt.plot(zseen, mags[m, :, 2]-mags[m, :, 4], styles[m], label=labels[m])

plt.legend(loc=0)
plt.suptitle("Comparison of slightly different exponential SFHs", fontsize=16)
plt.title("Using C09, Z=0.019, Chabrier IMF", fontsize=12)
plt.ylabel("r-z color")
plt.xlabel("Redshift")
plt.savefig("/Users/gbbtz7/GoogleDrive/Research/Plots/Misc/Comparing_Exponentials_C09.pdf", format="pdf")
