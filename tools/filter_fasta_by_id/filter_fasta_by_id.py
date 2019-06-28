#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fasta", dest="fasta", help="fasta to extract from")
    parser.add_argument("--list", dest="list", help="list of ids")
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

    for seq_id in seq_ids_to_extract:
        print(extracted_seqs[seq_id]['header'])
        for seq_segment in extracted_seqs[seq_id]['seq']:
            print(seq_segment)
    
if __name__ == '__main__':
    main()
