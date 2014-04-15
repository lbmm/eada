#!/bin/bash

# Script to loop over te sources in file test_sources.txt and test if they 
#  exist on some catalogues

FILE="test_sources.csv"

cats=$(python conesearch.py --list)
for cat in $cats
do
    echo "---"
    echo "-> Running searches for catalog $cat"
    while IFS=, read src ra dec
    do
        echo " -> looking for source $src ($ra , $dec)"
        python conesearch.py --catalog "$cat" --ra "$ra" --dec "$dec" --radius 5 --runit arcsec --short
        echo "-"
    done < ${FILE}
    echo "---"
    echo ""
done