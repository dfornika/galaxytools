#!/usr/bin/env python

from __future__ import print_function

import argparse

def main(args):

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("amino", help="MiCall amino.csv output file")
    parser.add_argument("--threshold", help="Threshold for calling")
    args = parser.parse_args()
    main(args)
