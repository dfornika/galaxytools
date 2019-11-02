#!/usr/bin/env python

from __future__ import print_function

import argparse
import errno
import csv
import os
import re
import shutil
import sys

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
        fieldnames = reader.fieldnames
    return fieldnames

def main(args):
    # create output directory
    try:
        os.mkdir(args.outdir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(args.outdir):
            pass
        else:
            raise

    # parse screening file
    screen = parse_screen_file(args.abricate_report_screening_file)
    contigs_with_genes_of_interest = []
    # parse all abricate reports and determine which ones contain genes of interest
    print("\t".join(["file", "gene_detected"]))
    for abricate_report in args.abricate_reports:
        gene_of_interest_detected = False
        with open(abricate_report, 'r') as f:
            abricate_report_reader = csv.DictReader(f, delimiter="\t", quotechar='"')
            for gene in screen:
                for abricate_report_row in abricate_report_reader:
                    if re.search(gene['regex'], abricate_report_row['GENE']):
                        gene_of_interest_detected = True
                        contigs_with_genes_of_interest.append(abricate_report_row['SEQUENCE'])
                f.seek(0)
                next(abricate_report_reader)
        print("\t".join([abricate_report, str(gene_of_interest_detected)]))

    # copy the corresponding plasmid fasta files into outdir        
    for contig in contigs_with_genes_of_interest:
        for plasmid in args.plasmids:
            copy_plasmid = False
            with open(plasmid, 'r') as f:
                for line in f:
                    if ('>' + contig) == line.rstrip():
                        copy_plasmid = True
            if copy_plasmid:
                print("\t".join([plasmid, "True"]))
                shutil.copy2(plasmid, args.outdir)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--plasmids", nargs='+', help="plasmid assemblies (fasta)")
    parser.add_argument("--abricate_reports", nargs='+', help="abricate reports (tsv)")
    parser.add_argument("--abricate_report_screening_file", help="")
    parser.add_argument("--outdir", dest="outdir", default=".", help="Output directory")
    args = parser.parse_args()
    main(args)
