RedshiftFinding
===============

Using stellar population synthesis models to find red sequence redshifts of galaxy clusters in the redshift range
0.5-1.5. It can start with images or catalogs. Only 2 bands are needed, as long as then span the 4000Å break at
redshift. This code currently handles r-z data, and will include [3.6] and [4.5] bands from IRAC soon. Additional bands
should not be too difficult to add if desired.

NOTE: This project is not near being finished, and its results are questionable at best for now. Don't expect great
things, or even reliable results at this stage.

____________________

Things to know while running the code:

1. The code looks for images, catalogs, and other things, as well as saves things like catalogs and plots to disk. In
the global_paths.py file, specify what directories you want for these various things.

2. The code can start at various locations, depending on whether or not you want to run SExtractor, just read from
catalogs, or start from a saved location once those things have been done.

3. In the fitting procedure (contained in the fit_z() function in the Cluster class in Cluster.py), there are many plots
created. The function can be passed a value to tell it not to plot anything. The individual plots can also be commented
out if you don't want certain plots.

_____

Needed packages:
ezgal (can be found at http://www.baryons.org/ezgal/)  You will also need at least one model set. It's currently set up 
to use BC03, but you can change that if desired.
    
numpy

matplotlib

mechanize

astropy

This code also asssumes you have a working copy of SExtractor. If not, this code will still be able to work with
catalogs, it just will not be able to make its own from images. In the main file, set START_WITH to 1 or larger.

