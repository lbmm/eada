
eada
====
External Archive Data Access: small pieces of code to query/retrieve (astronomical) data within the VO framework.

Tools
=====
-> conesearch.py : (CLI) script to search for sources in a set of catalogs (option '--list') given a position (ra,dec) and a radius

Dependencies
============
-> conesearch.py : depends on 'numpy (1.8.0)', 'astropy (0.3)' and 'pyvo (0.0beta2)'

[]
chb


dereddening
===========

 Code to compute and correct for reddening the flux given a magnitude value in 
one of the bands -- U, B, V, R, I, J, H, K -- between near-UV and IR.
 The code uses the reddening law of Cardelli et al. 1989 (published ApJ, 354, 245).

Dependencies
============

 The code uses only built-in python (2.7.6) modules -- argparse, logging, math.

