#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fasta", dest="fasta", help="fasta to extract from")
    parser.add_argument("--list", dest="list", help="list of ids")
    parser.add_argument("--separate", dest="separate", action="store_true", help="write to separate files")
    parser.add_argument("--outdir", dest="outdir", default=".", help="Output directory")
    args = parser.parse_args()
    
    extracted_seqs = {}

    seq_ids_to_extract = []

    with open(args.list) as f:
        for line in f:
            seq_ids_to_extract.append(line.strip())
    
    with open(args.fasta) as f:
        seq = []
        seq_id = ''
        header = ''
        for line in f:
            if line.startswith('>'):
                if seq:
                    extracted_seqs[seq_id] = {
                        'header': header,
                        'seq': seq,
                    }
                header = line.strip()
                seq = []
                seq_id = line.split()[0][1:]
            else:
                seq.append(line.strip())

    try:
        os.mkdir(args.outdir)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(args.outdir):
            pass
        else:
            raise

    for seq_id in seq_ids_to_extract:
        if args.separate:
            f = open(os.path.join(args.outdir, seq_id + ".fasta"), 'w+')
        else:
            f = open(os.path.join(args.outdir, "output.fasta"), 'w+')
        f.write(extracted_seqs[seq_id]['header'])
        for seq_segment in extracted_seqs[seq_id]['seq']:
            f.write(seq_segment)
        f.close()

if __name__ == '__main__':
    main()
