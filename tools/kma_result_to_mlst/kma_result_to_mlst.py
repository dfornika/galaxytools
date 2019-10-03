#!/usr/bin/env python

from __future__ import print_function

import argparse
import csv
import json
import os
import sys

from pprint import pprint


def main(args):
    LOCUS_ALLELE_DELIMITER = '_'
    
    res_fieldnames = [
        'template',
        'score',
        'expected',
        'template_length',
        'template_identity',
        'template_coverage',
        'query_identity',
        'query_coverage',
        'depth',
        'q_value',
        'p_value',
    ]
    
    with open(args.res, 'r') as f:
        loci = {}
        reader = csv.DictReader(f, fieldnames=res_fieldnames, dialect="excel-tab")
        next(reader) #skip header
        for row in reader:
            locus, allele = map(str.strip, row['template'].split(LOCUS_ALLELE_DELIMITER))
            if locus in loci:
                loci[locus][allele] = {
                    'score': int(row['score'].strip()),
                    'expected': int(row['expected'].strip()),
                    'template_length': int(row['template_length'].strip()),
                    'template_identity': float(row['template_identity'].strip()),
                    'template_coverage': float(row['template_coverage'].strip()),
                    'query_identity': float(row['query_identity'].strip()),
                    'query_coverage': float(row['query_coverage'].strip()),
                    'depth': float(row['depth'].strip()),
                    'q_value': float(row['q_value'].strip()),
                    'p_value': float(row['p_value'].strip()),
                }
            else:
                loci[locus] = {}
                loci[locus][allele] = {
                    'score': int(row['score'].strip()),
                    'expected': int(row['expected'].strip()),
                    'template_length': int(row['template_length'].strip()),
                    'template_identity': float(row['template_identity'].strip()),
                    'template_coverage': float(row['template_coverage'].strip()),
                    'query_identity': float(row['query_identity'].strip()),
                    'query_coverage': float(row['query_coverage'].strip()),
                    'depth': float(row['depth'].strip()),
                    'q_value': float(row['q_value'].strip()),
                    'p_value': float(row['p_value'].strip()),
                }
        print(json.dumps(loci))
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--res", dest="res", help="KMA result overview file")
    args = parser.parse_args()
    main(args)
