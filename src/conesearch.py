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
    in a given catalog. To see the available catalogs use the '--list' option.
"""

# List the available catalogs
def list_catalogs(cp):
    for k,d in cp.items():
        print k
        for c,v in d.items():
            print "| %-10s : %s" % (c,v)
        print ""

# Search a source in a particular catalog
def conesearch(ra,dec,radius,db_url,cp):
    """
    Search for objects inside the 'radius' around ('ra','dec,) in 'catalog'.
    
    Input:
        - ra      : right ascension (degrees)
        - dec     : declination (degrees)
        - radius  : search radius, value in degrees
        - catalog : options are 'sdss-7', '2mass', 'ukidss-8', 'usno-a2', 'usno-b1'
    """
    
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
        
    return res.votable

# --

def main(ra,dec,radius,db_url,columns,cp):
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

    srcsTab = conesearch(ra,dec,radius,db_url,cp).to_table()
    
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

    import config
    import string

    import argparse
    parser = argparse.ArgumentParser(description=desc)

    # Define the command line options
    parser.add_argument('--ra', dest='ra', type=float,
                        help="Right Ascension of the object (in degrees by default)")
    parser.add_argument('--dec', dest='dec', type=float,
                        help="Declination of the object (in degrees by default)")
    parser.add_argument('--radius', type=float, dest='radius',
                        help="Radius (around RA,DEC) to search for object(s)",)

    parser.add_argument('--runit', dest='runit', #default='arcsec',
                        help="Unit used for radius value. Choices are 'degree','arcmin','arcsec'.")

    parser.add_argument('--catalog', dest='cat',
                        help="Catalog to search for data. To see your choices use the '--list' option.")
    parser.add_argument('--url', dest='url',
                        help="Service URL to query. To see some options use the '--list' option.")
                        
    parser.add_argument('--columns', dest='cols', nargs='*',
                        help="Columns to get from the retrieved catalog. The argument 'asdc' will output a preset of columns, suitable for ASDC.\
                        If not given, all columns will be output.")

    parser.add_argument('--list', action='store_true',
                        help="Print the list os catalogs available for the search.")
    parser.add_argument('--short', action='store_true',
                        help="Just outputs if at least one source was found.")
                        
    parser.add_argument('-o','--outfile', dest='outfile', nargs='?', const='', default=None,
                        help="Filename to write the output, CSV format table file.")
    parser.add_argument('--nolog', action='store_true',
                        help="Do *not* log the events of the script. By default all events are written to 'conesearch.log' file.")

    # Parse the arguments
    args = parser.parse_args()
    
    cp = config.parse()
    if args.list:
        list_catalogs(cp)
        sys.exit(0)
    
    if not (args.ra and args.dec and args.radius and args.runit and (args.cat or args.url)):
        parser.print_help()
        print "---"
        if not args.ra:
            print(" RA not provided.")
        if not args.dec:
            print(" DEC not provided.")
        if not args.radius:
            print(" Radius not provided.")
        if not args.runit:
            print(" Radius unit (runit) not provided.")
        if not (args.cat or args.url):
            print(" Catalog/url not provided.")
        print "---"
        sys.exit(1)
        
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

    assert(args.cat or args.url)
    if not args.url and args.cat not in cp.keys():
        logging.critical("Wrong catalog name: %s", args.cat)
        print "Given catalog ('%s') is not known. Try a valid one (-h)." % (args.cat)
        print "Finishing here."
        sys.exit(1)

    if args.cat:
        cat = args.cat
        logging.debug("Catalog to search for sources: %s", cat)
        url = cp.get(cat)['url']
        logging.debug("Database (%s) url: %s", cat, url)
    else:
        url = args.url
        logging.debug("URL to search for sources: %s", url)

    if args.cols:
        if 'asdc' in args.cols:
            if args.url:
                cols = []
            else:
                dcat = cp.get(cat)
                if dcat.has_key('columns'):
                    cols = dcat.get('columns')
                    cols = string.split(cols,',')
                else:
                    cols = []
        else:
            cols = args.cols
    else:
        cols = []
    logging.debug("Columns to output: %s", cols)

    outfile = args.outfile
    if args.outfile is '':
        logging.warning("An empty name for output filename was given.")
        outfile = cat+'_'+str(ra)+'_'+str(dec)+'_'+str(radius)+'.csv'
        logging.warning("Filename for the output: %s" % outfile)
    logging.debug("Output file %s",outfile)
    
    # Now, the main function does the search and columns filtering...
    table = main(ra,dec,radius,url,cols,cp)
    
    if table is None:
        if args.short:
            print "Failed"
        else:
            print "---"
            print "\033[91mNot able to access data for source in archive %s\033[0m" % (cat)
            print "---"
        sys.exit(1)
    
    if args.short:
        print "OK"
        sys.exit(0)
    
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

