import ezgal

model = ezgal.ezgal("bc03_exp_1.0_z_0.02_chab_evolved_zf_3.0_ugriz.model")

print model.filename
print 'nages:', model.nages
print model.ages
print "nvs:", model.nvs
print "vs:", model.vs
print "ls:", model.ls
print "seds", model.seds
print "has masses:", model.has_masses
print "masses", model.masses
print "has sfh:", model.has_sfh
print "formation z:", model.zfs
print "filters:", model.filters
print "filter order:", model.filter_order
print "metadata:", model.meta_data