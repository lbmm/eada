from astropy.vo.client import conesearch as cone
from astropy.coordinates import ICRS
from astropy import units

import warnings

warnings.simplefilter("ignore")

def query_position(ra,dec,rad):
    #
    # cone diameter fraction in arcmin
    degfrac = 5
    rad = degfrac*units.arcsec
    
    #cone.list_catalogs()
    # Catalogs
    cats = {'sdss7' : 'SDSS DR7 - Sloan Digital Sky Survey Data Release 7 3'}
    cats.update({'2mass' : 'Two Micron All Sky Survey (2MASS) 2'})
    
    # sources to search for
    srcs = ['mrk421','3c273']
    
    # Loop over sources in each catalog
    for src in srcs:
        
        cd = ICRS.from_name(src)
        
        print "---"
        print "\033[37m-> source at (ra,dec): (%s,%s)\033[0m" % (cd.ra,cd.dec)
        print "---"
        for cat in cats.values():
            try:
                match = cone.conesearch(cd, rad, catalog_db=cat)
            except:
                print "---"
                print "\033[91mNot able to access data for source %s in archive %s\033[0m" % (src,cat)
                print "---"
                continue
            
            print "---"
            print "Found data for source \033[94m%s\033[0m in \033[92m%s\033[0m" % (src,cat)
            print " -> search radio: %s" % rad
            print " -> position of the source (ra,dec): \033[93m(%s,%s)\033[0m" % (cd.ra,cd.dec)
            print " Data [ra / dec]:"
            print zip(match.array['ra'].data, match.array['dec'])
            print "---"
            print match.array.dtype.names
        

#res.array.size
#res.array.dtype
#res.array.dtype.name
#res.array.dtype.names
#res.array
#res.array.dtype.names
#res.array['ra']

# Lets put a cli here, so that the script can work with free parameters
#

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('ra', help="Right Ascension of the object (in degrees by default)")
    parser.add_argument('dec', help="Declination of the object (in degrees by default)")
    parser.add_argument('--cUnit', help="Unit used on coordinates, RA *and* DEC. Default is 'degree'")
    parser.add_argument('radius', help="Radius (around RA,DEC) to search for object(s)")
    parser.add_argument('--rUnit', help="Unit used for radius value. Default is 'arcmin'")
    args = parser.parse_args()
    
    ra = args.ra
    dec = args.dec
    radius = args.radius
    out = query_position(ra,dec,radius)
    