#!/usr/bin/env python

from __future__ import print_function, division

import argparse
import csv
import errno
import json
import os
import re
import shutil
import sys

from pprint import pprint

MOB_TYPER_FIELDNAMES = [
        "file_id",
        "num_contigs",
        "total_length",
        "gc",
        "rep_type(s)",
        "rep_type_accession(s)",
        "relaxase_type(s)",
        "relaxase_type_accession(s)",
        "mpf_type",
        "mpf_type_accession(s)",
        "orit_type(s)",
        "orit_accession(s)",
        "PredictedMobility",
        "mash_nearest_neighbor",
        "mash_neighbor_distance",
        "mash_neighbor_cluster",
        "NCBI-HR-rank",
        "NCBI-HR-Name",
        "LitRepHRPlasmClass",
        "LitPredDBHRRank",
        "LitPredDBHRRankSciName",
        "LitRepHRRankInPubs",
        "LitRepHRNameInPubs",
        "LitMeanTransferRate",
        "LitClosestRefAcc",
        "LitClosestRefDonorStrain",
        "LitClosestRefRecipientStrain",
        "LitClosestRefTransferRate",
        "LitClosestConjugTemp",
        "LitPMIDs",
        "LitPMIDsNumber",
]

def parse_mob_typer_report(mob_typer_report_path):
    mob_typer_report = []

    with open(mob_typer_report_path) as f:
        reader = csv.DictReader(f, delimiter="\t", quotechar='"', fieldnames=MOB_TYPER_FIELDNAMES)
        for row in reader:
            mob_typer_report.append(row)
    return mob_typer_report

def parse_genbank_accession(genbank_path):
    with open(genbank_path, 'r') as f:
        while True:
            line = f.readline()
            if line.startswith('ACCESSION'):
                return line.strip().split()[1]

def parse_fasta_accession(fasta_path):
    with open(fasta_path, 'r') as f:
        while True:
            line = f.readline()
            if line.startswith('>'):
                return line.strip().split()[0][1:]

def count_fasta_contigs(fasta_path):
    contigs = 0
    with open(fasta_path, 'r') as f:
        for line in f:
            if line.startswith('>'):
                contigs += 1
    return contigs

def count_fasta_bases(fasta_path):
    bases = 0
    with open(fasta_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line.startswith('>'):
                bases += len(line)
    return bases

def compute_fasta_gc_percent(fasta_path):
    gc_count = 0
    total_bases_count = 0
    with open(fasta_path, 'r') as f:
        for line in f:
            if not line.startswith('>'):
                line = line.strip()
                line_c_count = line.count('c') + line.count('C')
                line_g_count = line.count('g') + line.count('G')
                line_total_bases_count = len(line)
                gc_count += line_c_count + line_g_count
                total_bases_count += line_total_bases_count
    return 100 * (gc_count / total_bases_count)

def main(args):

    # create output directory
    try:
        os.mkdir(args.outdir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(args.outdir):
            pass
        else:
            raise

    # parse mob_typer report
    mob_typer_report = parse_mob_typer_report(args.mob_typer_report)
    num_plasmid_contigs = count_fasta_contigs(args.plasmid)
    num_plasmid_bases = count_fasta_bases(args.plasmid)
    plasmid_gc_percent = compute_fasta_gc_percent(args.plasmid)
    
    with open(os.path.join(args.outdir, 'mob_typer_record.tsv'), 'w') as f:
        mob_typer_record_writer = csv.DictWriter(f, delimiter="\t", quotechar='"', fieldnames=MOB_TYPER_FIELDNAMES)
        mob_typer_record_writer.writeheader()
        for record in mob_typer_report:
            # match the plasmid against three properties in the MOB-Typer report:
            # 1. number of contigs
            # 2. total length of all contigs
            # 3. G/C percent (within +/-0.1%)
            if num_plasmid_contigs == int(record['num_contigs']) and \
               num_plasmid_bases == int(record['total_length']) and \
               abs(plasmid_gc_percent - float(record['gc'])) < 0.1: 
                for reference_plasmid in args.reference_plasmids_genbank:
                    if parse_genbank_accession(reference_plasmid) == record['mash_nearest_neighbor']:
                        shutil.copy2(reference_plasmid, os.path.join(args.outdir, "reference_plasmid.gbk"))

                for reference_plasmid in args.reference_plasmids_fasta:
                    if re.match(record['mash_nearest_neighbor'], parse_fasta_accession(reference_plasmid)) is not None:
                        shutil.copy2(reference_plasmid, os.path.join(args.outdir, "reference_plasmid.fasta"))
                mob_typer_record_writer.writerow(record)

    shutil.copy2(args.plasmid, os.path.join(args.outdir, "plasmid.fasta"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--plasmid", help="plasmid assembly (fasta)")
    parser.add_argument("--reference_plasmids_genbank", nargs='+', help="reference plasmids (genbank)")
    parser.add_argument("--reference_plasmids_fasta", nargs='+', help="reference plasmids (fasta)")
    parser.add_argument("--mob_typer_report", help="mob_typer reports (tsv)")
    parser.add_argument("--outdir", dest="outdir", default=".", help="Output directory")
    args = parser.parse_args()
    main(args)
