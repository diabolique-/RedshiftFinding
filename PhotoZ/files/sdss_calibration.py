def _call_sdss_sql(command, format="csv"):

    import urllib

    url = 'http://cas.sdss.org/public/en/tools/search/x_sql.asp?'

    params = urllib.urlencode({'cmd': command, 'format': format})  # fsql is command string
    my_file = urllib.urlopen(url + params)
    return my_file.readlines()

def make_sdss_catalog(min_ra, max_ra, min_dec, max_dec, bands):
    # TODO: see how bands are handled in the rest of my code to see the best way
    # to handle band information here. Probably be better with a list of bands
    # that need to be wrangled into the right form. This inplementation is
    # the simplest and stupidest way to do it.

    # TODO: document

    # Create command using templates. Basically, the things at the end replace the %s each time. The s indicates string.
    command = "select ra,dec,%s from PhotoObj where ra between %s and %s and dec between %s and %s and type=6" %(bands, min_ra, max_ra, min_dec, max_dec)
    # and r between 17.0 and 20.5 or z between 17.0 and 20.5
    # That mag cut didn't work when I tried implementing it for some reason
    lines = _call_sdss_sql(command)
    lines = [line.strip().split(",") for line in lines]

    # Now have list of lists that is like a table
    # Now need to write it to the file

    # TODO: check for errors from SDSS. File will start with ERROR
    # TODO: make this integrate with my actual file structure
    catalog = open("/Users/gbbtz7/Desktop/sdss.cat", "w")
    for line in lines:
        for thing in line:
            catalog.write(thing + " ")
        catalog.write("\n")

    catalog.close()



