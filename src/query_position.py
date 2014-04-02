from astropy.vo.client import conesearch as cone
from astropy.coordinates import ICRS
from astropy import units as u

import warnings

warnings.simplefilter("ignore")

def query_position(ra,dec,rad,ru):

    radius = rad*ru

    #cone.list_catalogs()
    # Catalogs
    cats = {'sdss7' : 'SDSS DR7 - Sloan Digital Sky Survey Data Release 7 3'}
    cats.update({'2mass' : 'Two Micron All Sky Survey (2MASS) 2'})
    
    c = ICRS(ra,dec,unit=(u.degree,u.degree))
    
    print "---"
    print "\033[37m-> source at (ra,dec): (%s,%s)\033[0m" % (c.ra,c.dec)
    print "---"
    for cat in cats.values():

        try:
            match = cone.conesearch(c, radius, catalog_db=cat)
        except:
            print "---"
            print "\033[91mNot able to access data for source in archive %s\033[0m" % (cat)
            print "---"
            continue
        
        print "---"
        print "Found data for source in \033[92m%s\033[0m" % (cat)
        print " -> search radio: %s" % radius
        print " -> position of the source (ra,dec): \033[93m(%s,%s)\033[0m" % (c.ra,c.dec)
        print " Data [ra / dec]:"
        print zip(match.array['ra'].data, match.array['dec'])
        print "---"    

#res.array.size
#res.array.dtype
#res.array.dtype.names

# Lets put a cli here, so that the script can work with free parameters
#
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('ra', help="Right Ascension of the object (in degrees by default)")
    parser.add_argument('dec', help="Declination of the object (in degrees by default)")
    parser.add_argument('radius', type=float,
                        help="Radius (around RA,DEC) to search for object(s)",)

#    parser.add_argument('--cUnit', choice=('degree','arcmin','arcsec'), default='degree',
#                        help="Unit used on coordinates, RA *and* DEC.'")
    parser.add_argument('--rUnit', default='arcsec',
                        help="Unit used for radius value. Choices are 'arcmin','arcsec'. Default is 'arcsec'.")
    args = parser.parse_args()
    
    ra = args.ra
    dec = args.dec
    radius = args.radius
    
    if args.rUnit == 'arcmin':
        ru = u.arcmin
    elif args.rUnit == 'arcsec':
        ru = u.arcsec
    else:
        raise ValueError("Radius' unit not valid. Try one of the choices: degree, arcmin, arcsec.")
    
    print ru
    out = query_position(ra,dec,radius,ru)
    
