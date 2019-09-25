#!/usr/bin/env python

from __future__ import print_function

import csv
import argparse

AMINO_ACIDS = ['A','C','D','E','F','G','H','I','K','L','M','N','P','Q','R','S','T','V','W','Y','*']

def determine_amino(amino_counts, threshold):
    amino = ""
    total_count = sum(amino_counts.values())
    amino_with_max_counts = sorted(amino_counts, key=amino_counts.get, reverse=True)[0]
    if total_count == 0:
        amino = "#"
    elif (amino_counts[amino_with_max_counts] / float(total_count)) > threshold:
        amino = amino_with_max_counts
    else:
        amino = "@"
    return amino

def determine_first_region(amino_file):
    with open(amino_file) as f:
        reader = csv.DictReader(f)
        row = next(reader)
        region = row['region']
    return region

def main(args):
    current_region = determine_first_region(args.amino)
    seq = []
    with open(args.amino) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['region'] == current_region:
                amino_counts = {}
                for amino_acid in AMINO_ACIDS:
                    amino_counts[amino_acid] = int(row[amino_acid])
                amino = determine_amino(amino_counts, args.threshold)
                seq.append(amino)
            else:
                print(">" + current_region)
                print(''.join(seq))
                current_region = row['region']
                seq = []
                amino_counts = {}
                for amino_acid in AMINO_ACIDS:
                    amino_counts[amino_acid] = int(row[amino_acid])
                amino = determine_amino(amino_counts, args.threshold)
                seq.append(amino)
        print(">" + current_region)
        print(''.join(seq))
                
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("amino", help="MiCall amino.csv output file")
    parser.add_argument("--threshold", default=0.15, type=float, help="Threshold for calling")
    args = parser.parse_args()
    main(args)
