#!/bin/bash

# Script to loop over te sources in file test_sources.txt and test if they 
#  exist on some catalogues

FILE="test_sources.csv"

# Tha catalog are:
cats='sdss 2mass usno'

while IFS=, read src ra dec
do
    echo ""
    echo "Testing the search for source $src ($ra , $dec)"
    echo "---"
    for cat in $cats
    do
        echo " -> on catalog $cat"
        python query_position.py -c "$cat" -r 5 --ra "$ra" --dec "$dec"
        echo "-"
    done
    echo "---"
done < ${FILE}
