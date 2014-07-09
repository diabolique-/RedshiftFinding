# Reads the file holding the equivalent redshifts, and makes a fit to the line, so we can interpolate slopes
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as polynomial
import numpy as np
import cPickle

# open the file
data = open("/Users/gbbtz7/GoogleDrive/Research/Data/equivalent_redshifts.dat", "r")

# Initialize empty list of equivalent redshifts, will append to it as file is read
redshifts = []

# REad in the data
for line in data:
    if not line.startswith("#"):  # avoid commented lines
        redshifts.append(float(line))
#redshifts will be in order of [U-V, B-R, V-I]

# make a list of known slopes of Coma (Eisenhard 2007). Same order as redshifts
slopes = [-0.122, -0.055, -0.029]
# Make a list of known errors of slopes (Eisenhardt 2007)
slope_errors = [0.01, 0.006, 0.005]
#turn these errors into weights
weights = [1/error for error in slope_errors]


# Find the best fit lines
quadratic_fit = polynomial.polyfit(redshifts, slopes, 2, w=weights)
linear_fit = polynomial.polyfit(redshifts, slopes, 1, w=weights)
# returns coefficients

# now turn these fits into a line
x = np.arange(0, 2.0, 0.01)

x = [round(i, 2) for i in x]

line = linear_fit[0] + x * linear_fit[1]
quadratic = quadratic_fit[0] + x*quadratic_fit[1] + (x**2)*quadratic_fit[2]

# # Plot points
# plt.errorbar(redshifts, slopes, slope_errors, c="k", fmt=".", markersize=10, label="Data")
# # Plot fit
# plt.plot(x, line, "r--", label="Linear fit")
# plt.plot(x, quadratic, "g--", label="Quadratic fit")
# plt.legend(loc=0)
# plt.xlabel("Redshift")
# plt.ylabel("Slope of Red Sequence")
# plt.suptitle("Slope of Red Sequence as a function of Redshift", fontsize=16)
# plt.title("Data from Eisenhardt 2007", fontsize=12)
# plt.savefig("/Users/gbbtz7/GoogleDrive/Research/Plots/RS_slope.pdf", format="pdf")

# Need to round x values, to eliminate floating point rounding errors
x = [round(i, 2) for i in x]


#Turn the better fit into a dictionary, for easier reference later
fit_dict = {x[i]: line[i] for i in range(len(x))}

print fit_dict

# Save the better fit to file
save_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/Best_fit_RS_slope.pickle", "w")
cPickle.dump(fit_dict, save_file, -1)