#!/usr/bin/env python

import sys
import logging
import warnings
warnings.simplefilter('ignore')

import pyvo as vo
from astropy import units
from astropy.table.table import Table

desc = """
    This script searchs for sources in a given position (RA,DEC) and radius (R) 
    in a given catalog. The catalogs available to search are:
    'sdss-7'
    '2mass'
    'ukidss-8'
    'usno-a2.0'
    'usno-a2'
    'usno-b1'
"""


# Databases of interest
catalogs = {
    'sdss-7Glx' : 'http://wfaudata.roe.ac.uk/sdssdr7-dsa/DirectCone?DSACAT=SDSS_DR7&DSATAB=Galaxy&',
    'sdss-7PhO' : 'http://wfaudata.roe.ac.uk/sdssdr7-dsa/DirectCone?DSACAT=SDSS_DR7&DSATAB=PhotoObj&',
    '2mass'    : 'http://wfaudata.roe.ac.uk/twomass-dsa/DirectCone?DSACAT=TWOMASS&DSATAB=twomass_psc&',
    'ukidss-8' : 'http://wfaudata.roe.ac.uk/ukidssDR8-dsa/DirectCone?DSACAT=UKIDSS_DR8&DSATAB=lasSource&',
    'usno-a2.0': 'http://archive.noao.edu/nvo/usno.php?cat=sa&',
    'usno-a2'  : 'http://www.nofs.navy.mil/cgi-bin/vo_cone.cgi?CAT=USNO-A2&',
    'usno-b1'  : 'http://www.nofs.navy.mil/cgi-bin/vo_cone.cgi?CAT=USNO-B1&'
}

def list_catalogs():
    print "Available options for 'catalogs':"
    for k,v in catalogs.items():
        print "-> %s : %s" % (k,v)

# Search for archives in registry
def search4catalogs(kw=[]):
    service = 'catalog'
    cats = vo.regsearch(keywords=kw,servicetype=service)
    return cats


# Search a source in a particular catalog
def conesearch(ra,dec,radius,catalog):
    """
    Search for objects inside the 'radius' around ('ra','dec,) in 'catalog'.
    
    Input:
        - ra      : right ascension (degrees)
        - dec     : declination (degrees)
        - radius  : search radius, value in degrees
        - catalog : options are 'sdss-7', '2mass', 'ukidss-8', 'usno-a2', 'usno-b1'
    """
    
    db_url = catalogs[catalog]
    logging.debug("Database (%s) url: %s", catalog, db_url)
    
    try:
        logging.debug("Position (%s,%s) and radius, in degrees, (%s)", ra, dec, radius)
        res = vo.conesearch( db_url, (ra,dec), radius, verbosity=3)
    except vo.dal.DALServiceError, e:
        logging.exception("Exception raised: %s", e)
        print "Service not responding"
        return None
    except vo.dal.DALQueryError, e:
        logging.exception("Exception raised: %s", e)
        print "Query returned error"
        return None
        
    if res.nrecs is 0:
        logging.error("No sources were found for (ra:%s, dec:%s ;radius:%s)", ra, dec, radius)
    else:
        logging.debug("Number of sources found: %d", res.nrecs)
        
    return res.votable.to_table()

# --

def main(ra,dec,radius,catalog,columns):
    """
    Do the input verifications and check the output of the query.
    
    Input:
        - ra      : right ascension (degree)
        - dec     : declination (degree)
        - radius  : radius to search for objects
        - catalog : catalog as given by the 'list_catalogs' function
        - columns : columns of interest to get from the output table
    """
    
    radius = rad.to(units.degree).value # convert the given radius to degrees

    srcsTab = conesearch(ra,dec,radius,catalog)
    
    if srcsTab is None:
        logging.critical("Search failed to complete. DAL raised an error.")
        print "Failed."
        return None

    # Garantee we don't have empty column names..
    cols = [ c for c in columns if c != '' ]
    if len(cols) > 0:
        srcsTab.keep_columns(cols)
    else:
        logging.warning("Since no column names were given, output will contain all catalog' columns.")
        
    return srcsTab

# --


# Lets put a cli here, so that the script can work with free parameters
#
if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description=desc)

    # Define the command line options
    parser.add_argument('--ra', dest='ra', type=float, required=True,
                        help="Right Ascension of the object (in degrees by default)")
    parser.add_argument('--dec', dest='dec', type=float, required=True,
                        help="Declination of the object (in degrees by default)")
    parser.add_argument('-r','--radius', type=float, dest='radius', required=True,
                        help="Radius (around RA,DEC) to search for object(s)",)

    parser.add_argument('--runit', default='arcsec', required=True,
                        help="Unit used for radius value. Choices are 'degree','arcmin','arcsec'.")

    parser.add_argument('--catalog', dest='cat', required=True,
                        help="Catalog to search for data. To see your choices use the '--list' option.")
    parser.add_argument('--columns', dest='cols', nargs='*',
                        help="Columns to get from the retrieved catalog. If not given, all columns will be output.")
                        
    parser.add_argument('-o','--outfile', dest='outfile', nargs='?', type=argparse.FileType('w'),
                        help="Filename to write the output, CSV format table file.")
    parser.add_argument('--nolog', action='store_true',
                        help="Do *not* log the events of the script. By default all events are written to 'conesearch.log' file.")

    # Parse the arguments
    args = parser.parse_args()
    
    if not args.nolog:
        logging.basicConfig(filename='conesearch.log', filemode='w',
                            format='%(levelname)s:%(message)s', level=logging.DEBUG)
    else:
        logging.setlevel(logging.NOTSET)

    ra = args.ra
    dec = args.dec
    logging.debug('RA:%s , DEC:%s', ra, dec)
    
    radius = args.radius
    if args.runit == 'degree':
        ru = units.degree
    elif args.runit == 'arcmin':
        ru = units.arcmin
    elif args.runit == 'arcsec':
        ru = units.arcsec
    else:
        logging.error("Radius' unit is not valid. Use 'degree', 'arcmin' or 'arcsec'.")
        sys.exit(1)
    rad = radius*ru
    logging.debug('Radius %s', rad)
    
    if args.cat not in catalogs.keys():
        logging.critical("Wrong catalog name: %s", args.cat)
        print "Given catalog ('%s') is not known. Try a valid one (-h)." % (args.cat)
        print "Finishing here."
        sys.exit(1)
    cat = args.cat
    logging.debug("Catalog to search for sources: %s", cat)
    
    cols = args.cols if args.cols else [] # cols can be empty
    logging.debug("Columns to output: %s", cols)

    if args.outfile is '':
        logging.error("Empty name for output filename.")
        sys.exit(1)
    outfile = args.outfile
        
    # Now, the main function does the search and columns filtering...
    table = main(ra,dec,radius,cat,cols)
    
    if table is None:
        print "---"
        print "\033[91mNot able to access data for source in archive %s\033[0m" % (cat)
        print "---"
        sys.exit(1)
        
    if len(cols) > 0:
        tab = table
        table = Table()
        for c in cols:
            table.add_column(tab.columns[c])

    if outfile:
        table.write(outfile,format='ascii',delimiter=',')

    print "---"
    print " Table retrieved:"    
    table.pprint(max_width=-1)
    print "---"

    sys.exit(0)
