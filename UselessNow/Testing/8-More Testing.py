import ezgal
import matplotlib.pyplot as plt
import numpy as np
import random

#make a model
model = ezgal.model('bc03_exp_0.1_z_0.02_chab_evolved_zf_5_riz.model')

# set star formation redshift
zForm = 5

# set ages to view galaxy at
#zSeen = model.get_zs(1.5) # redshift < 1.5
zSeen = np.arange(0.005, 1.9, 0.005)

# normalize to Coma
model.set_normalization(filter='ks', z=0.023, mag=10.9, apparent=True, vega=True)

# then calculate observables
# want r, i, z sloan bands
mag_r = model.get_apparent_mags(zf=zForm, filters='sloan_r', zs=zSeen)
mag_i = model.get_apparent_mags(zf=zForm, filters='sloan_i', zs=zSeen)
mag_z = model.get_apparent_mags(zf=zForm, filters='sloan_z', zs=zSeen)


# then find color
rz_color = mag_r - mag_z

# plot this, and save
plt.figure(figsize=(10,6))
plt.plot(zSeen, rz_color, 'k.')
plt.xlabel("Redshift")
plt.ylabel("Sloan r-z color")
plt.xticks(np.arange(plt.xlim()[0], plt.xlim()[1], 0.1))
plt.yticks(np.arange(plt.ylim()[0], plt.ylim()[1], 0.25))
plt.title("Using BC03, Exponential SFH (tau=0.1 gyr) starting at z=5, Z=0.02, Chabrier IMF", fontsize=10)
plt.suptitle("Sloan r-z Color vs Redshift", fontsize=18)
plt.subplots_adjust(left = 0.07, right = 0.98)
plt.savefig("test.pdf", format='pdf')

#make dictionary
color_mag_dict = dict()
for i in range(len(rz_color)):
    color_mag_dict[rz_color[i]] = zSeen[i]

#Test this
# write output to a f
file = open("Color-Redshift_Test.txt", 'w')
for i in range(0, 100):
    # now test with a random number
    random_color = random.uniform(min(rz_color), max(rz_color))
    # we want to find the closest
    # set closest match to blank, and closest value to 1000 (so it will be set, no matter what)
    lowestDiff = 1000
    closestColor = 0
    for color in color_mag_dict:
        if abs(random_color - color) < lowestDiff:
            lowestDiff = abs(random_color - color)
            closestColor = color
    # now that we have the closest color, print out color and predicted redshift
    random_color_str = str(random_color)
    redshift_str = str(color_mag_dict[closestColor])
    output = "Color: " + random_color_str + "\nRedshift: " + redshift_str + "\n\n"
    file.write(output)
