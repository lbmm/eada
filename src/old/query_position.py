import sys
import warnings
warnings.simplefilter("ignore")

from astropy.vo.client import conesearch as cone
from astropy.coordinates import ICRS
from astropy import units as u

#cone.list_catalogs()
descr = """
    This script searchs for sources in a given position (RA,DEC) and radius (R) 
    in a given catalog. The catalogs available to search are:
    'sdss'
    '2mass'
    'usno'
"""

catalogs = {
    'sdss'    : 'SDSS DR7 - Sloan Digital Sky Survey Data Release 7 3',
    '2mass'   : 'Two Micron All Sky Survey (2MASS) 2',
    'usno-a2' : 'USNO-A2.0 1'
}

columns = {
    'sdss'    : ['objID','run','rerun','camcol','field','obj','type','ra','dec','u','g','r','i','z','err_u','err_g','err_r','err_i','err_z'],
    '2mass'   : ['ra', 'dec', 'htmID', 'h_m', 'j_m', 'k_m', 'h_msigcom', 'j_msigcom', 'k_msigcom'],
    'usno-a2' : ['Catalog_Name', 'RA', 'DEC', 'B_Magnitude', 'R_Magnitude'] # DISTANCE, PA
}

def list_catalogs():
    print "Available options for 'catalogs':"
    for k,v in catalogs.items():
        print "-> %s : %s" % (k,v)
    

def query_position(ra,dec,rad,ru,cat,cols):

    radius = rad*ru
    
    c = ICRS(ra,dec,unit=(u.degree,u.degree))
    
    print "---"
    print "\033[37m-> Looking for source(s) [%s] around (ra=%s,dec=%s)\033[0m" % (radius,c.ra,c.dec)
    print "---"

    try:
        match = cone.conesearch(c, radius, catalog_db=cat)
    except:
        return None
        
    tab = match.to_table()
    tab.keep_columns(cols)
    return tab
    

# Lets put a cli here, so that the script can work with free parameters
#
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()

    parser.add_argument('--ra', dest='ra', required=True,
                        help="Right Ascension of the object (in degrees by default)")
    parser.add_argument('--dec', dest='dec', required=True,
                        help="Declination of the object (in degrees by default)")
    parser.add_argument('-r','--radius', type=float, dest='radius', required=True,
                        help="Radius (around RA,DEC) to search for object(s)",)

    parser.add_argument('--rUnit', default='arcsec',
                        help="Unit used for radius value. Choices are 'arcmin','arcsec'. Default is 'arcsec'.")

    parser.add_argument('-c','--catalog', dest='cat', required=True,
                        help="Catalog to search for data. To see your choices use the '--list' option.")
                        
    args = parser.parse_args()
    ra = args.ra
    dec = args.dec
    radius = args.radius
    
    if args.rUnit == 'arcmin':
        ru = u.arcmin
    elif args.rUnit == 'arcsec':
        ru = u.arcsec
    else:
        raise ValueError("Radius' unit not valid. Use 'arcmin' or 'arcsec'.")

    
    if args.cat not in catalogs.keys():
        raise ValueError("Catalog is not known. Try a valid one (-h).")
    cat = catalogs[args.cat]
    cols = columns[args.cat]
    
    table = query_position(ra,dec,radius,ru,cat,cols)
    
    if table is None:
        print "---"
        print "\033[91mNot able to access data for source in archive %s\033[0m" % (cat)
        print "---"
        sys.exit(1)
    else:
        print "---"
        print " Table retrieved:"
        table.pprint(max_width=-1)
        print "---"
        sys.exit(0)
