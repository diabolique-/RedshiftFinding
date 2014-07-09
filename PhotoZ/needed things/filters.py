# holds functions dealing with filter operations. Used to calculate slope of CMR

# It's a little sloppy. This is only used to create the file with effective wavelenths.
import collections
import matplotlib.pyplot as plt

#def find_effective_wavelength():
# Open file for reading
Eisenhardt_data = open("/Users/gbbtz7/GoogleDrive/Research/Data/Eisenhardt2007filters", "r")
sloan_r_data = open("/Library/Python/2.7/site-packages/ezgal/data/filters/sloan_r", "r")
sloan_z_data = open("/Library/Python/2.7/site-packages/ezgal/data/filters/sloan_z")

# Initialize empty ordered dictionaries that will store the information for each filter
# Keys are wavelength, values are filter response at that wavelength
U, B, V, R, I, z, J, H, ks, sloan_r, sloan_z = collections.OrderedDict(), collections.OrderedDict(), \
                                               collections.OrderedDict(), collections.OrderedDict(), \
                                               collections.OrderedDict(), collections.OrderedDict(), \
                                               collections.OrderedDict(), collections.OrderedDict(), \
                                               collections.OrderedDict(), collections.OrderedDict(), \
                                               collections.OrderedDict()

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
for line in sloan_r_data:
    sloan_r[float(line.split()[0])] = float(line.split()[1])

for line in sloan_z_data:
    sloan_z[float(line.split()[0])] = float(line.split()[1])

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
filter_list = [U, B, V, R, I, z, sloan_r, sloan_z] # excluded some to make life easier
# Make a list of string that will be used late to write these to the file
filter_list_names = ["U", "B", "V", "R", "I", "z", "Sloan_r", "Sloan_z"]

# OPen a file for writing, will put filter effective wavelengths there as we go
file = open("/Users/gbbtz7/GoogleDrive/Research/Data/Eisenhardt2007filters_effective.dat", "w")


# set up a figure
fig = plt.figure(figsize=(15, 5))
ax = fig.add_subplot(1, 1, 1)
fig.subplots_adjust(left=0.08, right=0.94)

colors = ["r", "0.4", "b", "c", "m", "y", "k", "g", "g", "0.8", "k"]


# Now can find effective wavelengths
i = 0 # counter for plotting
for f in filter_list:
    # basically find "center of mass" = sum(wavelength * response) / sum(response)
    top, bottom = 0, 0
    for w in f:
        top += w * f[w]
        bottom += f[w]
    effective_wavelength = top/bottom

    # Write to the file
    file.write(filter_list_names[i] + "\t" + str(effective_wavelength) + "\n")

    # Plot the filter response curve
    ax.plot(f.keys(), f.values(), c=colors[i], label=filter_list_names[i])

    # Add a vertical line at the right place for the effective wavelength
    ax.axvline(effective_wavelength, c=colors[i], linestyle="--")
    i += 1

plt.legend(loc=0)
ax.set_ylim([0, 1.0])

# Add titles and labels
ax.set_title("Filter Response Curves and Effective Wavelength from Eisenhardt 2007")
ax.set_ylabel("Response")
ax.set_xlabel("Wavelength [Angstroms]")
#ax.set_xlim([3000, 10000])
fig.savefig("/Users/gbbtz7/GoogleDrive/Research/Plots/filter_response.pdf", format="pdf")






file.close()



