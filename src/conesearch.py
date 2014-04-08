#!/usr/bin/env python

import sys
import warnings

import pyvo as vo


# Databases of interest
db_url = {
    #http://registry.astrogrid.org/astrogrid-registry/services/RegistryQueryv1_0
    'sdss-7'   : 'http://wfaudata.roe.ac.uk/sdssdr7-dsa/DirectCone?DSACAT=SDSS_DR7&DSATAB=Galaxy&',
    '2mass'    : 'http://wfaudata.roe.ac.uk/twomass-dsa/DirectCone?DSACAT=TWOMASS&DSATAB=twomass_psc&',
    'ukidss-8' : 'http://wfaudata.roe.ac.uk/ukidssDR8-dsa/DirectCone?DSACAT=UKIDSS_DR8&DSATAB=lasSource&',
    'usno-a2.0': 'http://archive.noao.edu/nvo/usno.php?cat=a&',
    'usno-a2'  : 'http://www.nofs.navy.mil/cgi-bin/vo_cone.cgi?CAT=USNO-A2&',
    'usno-b1'  : 'http://www.nofs.navy.mil/cgi-bin/vo_cone.cgi?CAT=USNO-B1&'
}

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
        - ra : right ascension (degrees)
        - dec : declination (degrees)
        - radius : search radius (degrees)
        - catalog : options are 'sdss-7', '2mass', 'ukidss-8', 'usno'
    """
    
    try:
        res = vo.conesearch( db_url[catalog], (ra,dec), radius, verbosity=3)
    except vo.dal.DALServiceError, e:
        print "Service not responding"
        return None
    except vo.dal.DALQueryError, e:
        print "Query returned error"
        return None
        
    return res.votable.to_table()
    

def main(ra,dec,radius,catalog,output_columns)