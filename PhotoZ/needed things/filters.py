# holds functions dealing with filter operations. Used to calculate slope of CMR

# It's a little sloppy. This is only used to create the file with effective wavelenths.
import collections
from scipy.integrate import simps
import matplotlib.pyplot as plt
import numpy as np
from PhotoZ import global_paths
from PhotoZ import config_data

#def find_effective_wavelength():
# Open file for reading
Eisenhardt_data = open(global_paths.home_directory + "data/Eisenhardt2007filters.txt", "r")


# Initialize empty ordered dictionaries that will store the information for each filter
# Keys are wavelength, values are filter response at that wavelength
U, B, V, R, I, z, J, H, ks = collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), \
                             collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict(), \
                             collections.OrderedDict(), collections.OrderedDict(), collections.OrderedDict()

# Read in the data
for line in Eisenhardt_data:
    if not line.startswith("#"):  # Ignore comments at beginning
        # Split the line for easier parsing
        line = line.split()
        # Choose which filter the line belongs to, and add the data to the corresponding dictionary
        if line[0] == "U":
            U[int(line[1])] = float(line[2])
        elif line[0] == "B":
            B[int(line[1])] = float(line[2])
        elif line[0] == "V":
            V[int(line[1])] = float(line[2])
        elif line[0] == "R":
            R[int(line[1])] = float(line[2])
        elif line[0] == "I":
            I[int(line[1])] = float(line[2])
        elif line[0] == "z":
            z[int(line[1])] = float(line[2])
        elif line[0] == "J":
            J[int(line[1])] = float(line[2])
        elif line[0] == "H":
            H[int(line[1])] = float(line[2])
        elif line[0] == "K_S_":
            ks[int(line[1])] = float(line[2])
        else:
            print line, "WHOOPS!!!!!!"

# # Want to normalize the 2 sloan ones to 1 for better comparison.
# max_r, max_z = 0, 0
# for w in sloan_z:
#     if sloan_z[w] > max_z:
#         max_z = sloan_z[w]
# for w in sloan_z:
#     sloan_z[w] /= max_z
#
# for w in sloan_r:
#     if sloan_r[w] > max_r:
#         max_r = sloan_r[w]
# for w in sloan_r:
#     sloan_r[w] /= max_r



# turn all these dictionaries into a list
filter_list = [U, B, V, R, I, z, J, H, ks] # excluded some to make life easier
# Make a list of string that will be used late to write these to the file
filter_list_names = ["U", "B", "V", "R", "I", "z", "J", "H", "K"]

# OPen a file for writing, will put filter effective wavelengths there as we go
file = open(global_paths.home_directory + "data/Eisenhardt2007_filters_pivot.txt", "w")


# set up a figure
fig = plt.figure(figsize=(15, 11))
e_ax = plt.subplot2grid((2,1), (0, 0))
fig.subplots_adjust(left=0.08, right=0.94)

colors = ["r", "g", "0.4", "b", "c", "m", "y", "k", "g", "0.8", "0.1", "r", "g", "b", "c", "m", ]


# Now can find effective wavelengths
i = 0 # counter for plotting
for f in filter_list:
    # calculate the pivot wavelength
    response = [float(x) for x in f.values()]
    wavelengths = [float(l) for l in f.keys()]
    numerator = [response[k] * wavelengths[k] for k in range(len(response))]
    denominator = [response[k] / wavelengths[k] for k in range(len(response))]
    pivot = np.sqrt((simps(numerator, wavelengths))/simps(denominator, wavelengths))


    # Write to the file
    file.write(filter_list_names[i] + "\t" + str(pivot) + "\n")

    # Plot the filter response curve
    e_ax.semilogx(f.keys(), f.values(), c=colors[i], label=filter_list_names[i])

    # Add a vertical line at the right place for the effective wavelength
    e_ax.axvline(pivot, c=colors[i], linestyle="--")
    i += 1
# Add titles and labels
e_ax.set_title("Eisenhardt")
e_ax.set_ylabel("Response")
e_ax.set_xlabel("Wavelength [Angstroms]")
plt.legend(loc=0)
e_ax.set_ylim([0, 1.0])


# do this for science filters
ax =plt.subplot2grid((2,1), (1, 0))

filter_list = config_data.filters_list
filters_path = "/usr/local/scisoft/packages/python/lib/python2.6/site-packages/ezgal/data/filters/" # may need to change
for i, f in enumerate(filter_list):
    filter_file = open(filters_path + f)
    wavelengths, respones = [], []
    for line in filter_file:
        wavelengths.append(float(line.split()[0]))
        respones.append(float(line.split()[1]))

    # normalize respones
    respones = [r / max(respones) for r in respones]

    numerator = [respones[k] * wavelengths[k] for k in range(len(respones))]
    denominator = [respones[k] / wavelengths[k] for k in range(len(respones))]
    pivot = np.sqrt((simps(numerator, wavelengths))/simps(denominator, wavelengths))
    # Plot the filter response curve
    ax.semilogx(wavelengths, respones,c=colors[i], label=f, linewidth=1.5)

    # Add a vertical line at the right place for the effective wavelength
    ax.axvline(pivot, c=colors[i], linestyle="--")
    i += 1


plt.legend(loc=0)
ax.set_ylim([0, 1.0])

# Add titles and labels
ax.set_title("Others")
ax.set_ylabel("Response")
ax.set_xlabel("Wavelength [Angstroms]")
#ax.set_xlim([3000, 10000])
fig.savefig("/Users/gbbtz7/GoogleDrive/Research/Plots/filter_response.pdf", format="pdf")









file.close()



