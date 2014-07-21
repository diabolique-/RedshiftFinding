from PhotoZ.files import  main_functions
import ezgal
import  matplotlib.pyplot as plt

images = main_functions.read_cluster_objects()

for i in images:
    ras = [gal.ra for gal in i.galaxy_list]
    decs = [gal.dec for gal in i.galaxy_list]
    plt.scatter(ras, decs)
    plt.title(i.name)
    plt.show()
