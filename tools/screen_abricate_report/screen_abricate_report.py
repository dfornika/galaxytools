#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import re
import sys
import csv
from pprint import pprint

def parse_screen_file(screen_file):
    screen = []
    with open(screen_file) as f:
        reader = csv.DictReader(f, delimiter="\t", quotechar='"')
        for row in reader:
            screen.append(row)
    return screen

def get_abricate_report_fieldnames(abricate_report):
    with open(abricate_report) as f:
        reader = csv.DictReader(f, delimiter="\t", quotechar='"')
        row = next(reader)
    fieldnames = row.keys()
    return fieldnames
    
def main(args):
    screen = parse_screen_file(args.screen)
    abricate_report_fieldnames = get_abricate_report_fieldnames(args.abricate_report)
    with open(args.abricate_report) as f:
        reader = csv.DictReader(f, delimiter="\t", quotechar='"')
        writer = csv.DictWriter(sys.stdout, delimiter="\t", quotechar='"', fieldnames=abricate_report_fieldnames)
        writer.writeheader()
        for row in reader:
            for gene in screen:
                if re.search(gene['regex'], row['GENE']):
                    writer.writerow(row)
        


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--screen", help="TSV file defining genes to screen for")
    parser.add_argument("abricate_report", help="Abricate output")
    args = parser.parse_args()
    main(args)
