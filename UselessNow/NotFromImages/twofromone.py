import math

r_cat = open("/Users/gbbtz7/Astro/SExtractor/m1636p1019.r.cat")
r_lines = [line.split() for line in r_cat.readlines() if not line.startswith("#")]
z_cat = open("/Users/gbbtz7/AStro/SExtractor/m1636p1019.z.cat")
z_lines = [line.split() for line in z_cat.readlines() if not line.startswith("#")]

catalog_file = open("/Users/gbbtz7/GoogleDrive/Research/Data/ClusterData/m1636p1029.phot.cat", "w")
catalog_file.write("# id         ra          dec      zmag     rmz     rmze\n#")

for r_line, z_line in zip(r_lines, z_lines):
    # if int(r_line[-2]) < 4 and int(z_line[-2]) < 4:
        id_num = r_line[0]
        ra = z_line[1]
        dec = z_line[2]
        z_mag = z_line[3]
        z_mag_err = z_line[4]
        r_mag = r_line[1]
        r_mag_err = r_line[2]
        rmz = float(r_mag) - float(z_mag)
        rmz_error = math.sqrt((float(r_mag_err))**2 + (float(z_mag_err))**2)
        catalog_file.write(str(id_num) + "     " + str(ra) + "     " + str(dec) + "    " + str(round(float(z_mag), 2)
                                                                                                     ) + "     " +
                           str(round(float(rmz), 2)) + "     " + str(round(float(rmz_error), 2)) + "\n")
