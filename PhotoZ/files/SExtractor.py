import os
import subprocess


os.chdir(sextractor_params_directory)
# TODO: use "which sex" to find the place SExtractor is. I use where mine is, but that may change.
# TODO: after using "which sex", make it notice if SExtractor is not on the machine.
subprocess.call(["/usr/local/scisoft///bin/sex", "/Users/gbbtz7/Astro/Data/gem/2013B/MOO0024+3303/MOO0024+3303_r.fits", "-c", "gmos.r.sex"])
