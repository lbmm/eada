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

# Databases of interest
catalogs = {
    'sdss-dr7': 'http://wfaudata.roe.ac.uk/sdssdr7-dsa/DirectCone?DSACAT=SDSS_DR7&DSATAB=PhotoObj&',
    '2mass'    : 'http://wfaudata.roe.ac.uk/twomass-dsa/DirectCone?DSACAT=TWOMASS&DSATAB=twomass_psc&',
    'ukidss-dr8' : 'http://wfaudata.roe.ac.uk/ukidssDR8-dsa/DirectCone?DSACAT=UKIDSS_DR8&DSATAB=lasSource&',
    'usno-a2': 'http://archive.noao.edu/nvo/usno.php?cat=sa&'
}
#    'sdss-dr7': 'http://wfaudata.roe.ac.uk/sdssdr7-dsa/DirectCone?DSACAT=SDSS_DR7&DSATAB=Galaxy&',
#    'usno-a2.1'  : 'http://www.nofs.navy.mil/cgi-bin/vo_cone.cgi?CAT=USNO-A2&',
#    'usno-a2.2': 'http://vizier.u-strasbg.fr/viz-bin/votable/-A?-source=I/252/out&',
#    'usno-a2.3': 'http://vo.astronet.ru/sai_cas/conesearch?cat=usnoa2&tab=main&',
#    'usno-b1'  : 'http://www.nofs.navy.mil/cgi-bin/vo_cone.cgi?CAT=USNO-B1&',
#    'usno-b1.1': 'http://vizier.u-strasbg.fr/viz-bin/votable/-A?-source=I/284/out&',
#    'usno-b1.2': 'http://vo.astronet.ru/sai_cas/conesearch?cat=usnob1&tab=main&'

columns = {
    'sdss-dr7'  : ['objID', 'run', 'rerun', 'camcol', 'field', 'obj', 'type', 'ra', 'dec', 'u', 'g', 'r', 'i', 'z', 'err_u', 'err_g', 'err_r', 'err_i', 'err_z'],
    '2mass'   : ['ra', 'dec', 'htmID', 'h_m', 'j_m', 'k_m', 'h_msigcom', 'j_msigcom', 'k_msigcom'],
    'usno-a2' : ['Catalog_Name', 'RA', 'DEC', 'B_Magnitude', 'R_Magnitude', 'Distance', 'Position_Angle'],
#    'usno-b1' : ['Catalog_Name', 'RA', 'DEC', 'B_Magnitude', 'R_Magnitude'],
    'ukidss-dr8': ['sourceID', 'ra', 'dec', 'epoch', 'eBV', 'yAperMag3', 'yAperMag3Err', 'j_1AperMag3', 'j_1AperMag3Err', 'hAperMag3', 'hAperMag3Err', 'kAperMag3', 'kAperMag3Err']
}

# List the available catalogs
def list_catalogs():
    #print "Available options for 'catalogs':"
    for k,v in catalogs.items():
        print "%s" % (k)


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
        
    return res.votable

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

    srcsTab = conesearch(ra,dec,radius,catalog).to_table()
    
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
    parser.add_argument('--ra', dest='ra', type=float,
                        help="Right Ascension of the object (in degrees by default)")
    parser.add_argument('--dec', dest='dec', type=float,
                        help="Declination of the object (in degrees by default)")
    parser.add_argument('--radius', type=float, dest='radius',
                        help="Radius (around RA,DEC) to search for object(s)",)

    parser.add_argument('--runit', default='arcsec',
                        help="Unit used for radius value. Choices are 'degree','arcmin','arcsec'.")

    parser.add_argument('--catalog', dest='cat',
                        help="Catalog to search for data. To see your choices use the '--list' option.")
    parser.add_argument('--columns', dest='cols', nargs='*',
                        help="Columns to get from the retrieved catalog. If not given, all columns will be output.")

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
    
    if args.list:
        list_catalogs()
        sys.exit(0)
        
    if not args.ra:
        print("error: RA not provided.")
        sys.exit(1)
    if not args.dec:
        print("error: DEC not provided.")
        sys.exit(1)
    if not args.radius:
        print("error: Radius not provided.")
        sys.exit(1)
    if not args.runit:
        print("error: Radius unit (runit) not provided.")
        sys.exit(1)
    if not args.cat:
        print("error: Catalog not provided.")
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
    
    if args.cat not in catalogs.keys():
        logging.critical("Wrong catalog name: %s", args.cat)
        print "Given catalog ('%s') is not known. Try a valid one (-h)." % (args.cat)
        print "Finishing here."
        sys.exit(1)
    cat = args.cat
    logging.debug("Catalog to search for sources: %s", cat)

    if args.cols:
        if 'asdc' in args.cols:
            cols = columns[cat]
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
    table = main(ra,dec,radius,cat,cols)
    
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
