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

def get_fieldnames(input_file):
    with open(input_file) as f:
        reader = csv.DictReader(f, delimiter="\t", quotechar='"')
        row = next(reader)
    fieldnames = row.keys()
    return fieldnames
    
def main(args):
    screen = parse_screen_file(args.screening_file)
    abricate_report_fieldnames = get_fieldnames(args.abricate_report)
    gene_detection_status_fieldnames = ['gene_name', 'detected']
    with open(args.abricate_report, 'r') as f1, open(args.screened_report, 'w') as f2, open(args.gene_detection_status, 'w') as f3:
        abricate_report_reader = csv.DictReader(f1, delimiter="\t", quotechar='"')
        screened_report_writer = csv.DictWriter(f2, delimiter="\t", quotechar='"', fieldnames=abricate_report_fieldnames)
        gene_detection_status_writer = csv.DictWriter(f3, delimiter="\t", quotechar='"', fieldnames=gene_detection_status_fieldnames)
        screened_report_writer.writeheader()
        gene_detection_status_writer.writeheader()

        for gene in screen:
            gene_detection_status = {
                'gene_name': gene['gene_name'],
                'detected': False
            }
            for abricate_report_row in abricate_report_reader:
                if re.search(gene['regex'], abricate_report_row['GENE']):
                    gene_detection_status['detected'] = True
                    screened_report_writer.writerow(abricate_report_row)
            gene_detection_status_writer.writerow(gene_detection_status)
            f1.seek(0) # return file pointer to start of abricate report


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("abricate_report", help="Input: Abricate report to screen (tsv)")
    parser.add_argument("--screening_file", help="Input: List of genes to screen for (tsv)")
    parser.add_argument("--screened_report", help="Output: Screened abricate report including only genes of interest (tsv)")
    parser.add_argument("--gene_detection_status", help="Output: detection status for all genes listed in the screening file (tsv)")
    args = parser.parse_args()
    main(args)
