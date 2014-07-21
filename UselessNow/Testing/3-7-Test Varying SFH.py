import ezgal
import matplotlib.pyplot as plt

# load ezgal model f
model = ezgal.model( 'bc03_ssp_z_0.02_chab.model' )

#exp_1 = ezgal.model('AAAbc03_exp_1.0_delay_3.0_z_0.02_chab.model')
#exp_5 = ezgal.model('AAAbc03_exp_5.0_z_0.02_chab.model')
#exp_combo = ezgal.model('AAAbc03_exp_5.0_+_exp_1.0_delay_3.0_z_0.02_chab.model')
#now generate two CSPs with tau = 1.0 and 5.0 (Gyrs)
exp_1 = model.make_exponential(1.0)
exp_5 = model.make_exponential(5.0)
# Delay one by 3 gyrs
exp_1 = exp_1.make_delayed(3.0)

# make a custom SFH: need lists of ages and SFH
ages = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
SFH = [5, 6, 7, 5, 2, 5, 0, 2, 4, 0, 0]
custom = model.make_numeric(ages, SFH, age_units='gyrs')

# Weight things before adding together into complicated one
exp_1 = exp_1.weight(1)
exp_5 = exp_5.weight(3)
custom = custom.weight(4)


combo = exp_1 + exp_5 + custom

#exp_1.save_model('AAAbc03_exp_1.0_delay_3.0_z_0.02_chab.model')
#exp_5.save_model('AAAbc03_exp_5.0_z_0.02_chab.model')
#exp_combo.save_model('AAAbc03_exp_5.0_+_exp_1.0_delay_3.0_z_0.02_chab.model')


# now plot age versus absolute mag
# ezgal does everything in redshift space, so we first have to get some redshifts
zf = 3.0
zs = model.get_zs( zf )
ages = model.get_age( zf, zs )

# and plot
plt.figure(figsize=(16, 7))
plt.subplot(1, 2, 1)
plt.plot( ages, exp_1.get_absolute_mags( zf, filters='sloan_i', zs=zs ), 'k--', label='Tau = 1.0 gyrs, delayed' )
plt.plot( ages, exp_5.get_absolute_mags( zf, filters='sloan_i', zs=zs ), 'k-.', label='Tau = 5.0 gyrs' )
plt.plot( ages, combo.get_absolute_mags( zf, filters='sloan_i', zs=zs ), 'k:', label='Combination' )
plt.plot(ages, custom.get_absolute_mags( zf, filters='sloan_i', zs=zs ), 'k-', label='Custom' )

# some labels
plt.xlabel( 'Age (Gyrs)' )
plt.ylabel( 'Absolute Mag (Sloan i)' )
plt.title('Absolute Magnitude vs Age of varying SFHs')
plt.legend(loc=0)

# plot star formation rate
plt.subplot( 1,2,2 )
exp1_ages = ezgal.utils.convert_time( exp_1.ages, incoming='years', outgoing='gyrs' )
exp5_ages = ezgal.utils.convert_time( exp_5.ages, incoming='years', outgoing='gyrs' )
custom_ages = ezgal.utils.convert_time( custom.ages, incoming='years', outgoing='gyrs' )
exp_combo_ages = ezgal.utils.convert_time(combo.ages, incoming='years', outgoing='gyrs')
plt.plot( exp1_ages, exp_1.sfh/8, 'k--', label='Exponential: Tau = 1.0 gyrs, delayed 3 gyrs' )
plt.plot( exp5_ages, exp_5.sfh/2.66666, 'k-.', label='Exponential: Tau = 5.0 gyrs' )
plt.plot(custom_ages, custom.sfh/2, 'k:', label='custom')
plt.plot(exp_combo_ages, combo.sfh, 'k-', label='Combination')

# some labels
plt.xlabel( 'Age (Gyrs)' )
plt.ylabel( 'SFR' )
plt.legend(loc=0)
plt.text(10, .12, "Weights \nTau = 1 gyr: 1\nTau = 5 gyrs: 3\nCustom: 4", bbox=dict())
plt.title('Star Formation rate of varying Star Formation Histories')
plt.suptitle("BC03, Z=0.02, Chabrier IMF", fontsize=12)
plt.subplots_adjust(left = 0.05, right = 0.99, wspace=0.20)

plt.savefig('test.pdf', format='pdf')


#Note: no normalization, and magnitudes are absolute