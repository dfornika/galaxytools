#!/usr/bin/env python

import argparse
import json
from pprint import pprint

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--label', dest='label',
                        help='A human-readable label for the bin')
    parser.add_argument('accessions_file',
                        help='File containing a list of accessions (one accession per line)')

    args = parser.parse_args()
    return args



def main(args):

    output = {}

    output['label'] = args.label

    with open(args.accessions_file, 'r') as f:
        accessions = [line.rstrip() for line in f]

    output['accessions'] = accessions
    print(json.dumps(output))
    
if __name__ == '__main__':
    args = parse_args()
    main(args)
