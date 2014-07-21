import ezgal
import numpy as np

##################################################################
## CAN CHANGE THIS
model = ezgal.ezgal("m05_ssp_z_0.02_krou.model")
##################################################################


# Set formation redshift and observed redshifts
zf = 3.0
zs = np.arange(0.5, 1.5000001, 0.01)

# Normalize to Coma
model.set_normalization(filter='ks', mag=10.9, apparent=True, vega=True, z=0.023)

# Calculate observables
mags = model.get_apparent_mags(zf, filters=["sloan_r", "sloan_i", "sloan_z", "ch1", "ch2"], zs=zs, vega=False)

##################################################################
## CAN CHANGE THIS
# Save model
model.save_model("/Library/Python/2.7/site-packages/ezgal/data/models/m05_ssp_z_0.02_krou_evolved_zf_3.0_ugrizch1ch2"
                 ".model")
##################################################################