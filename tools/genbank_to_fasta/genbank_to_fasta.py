#!/usr/bin/env python

import socket
import sys
from Bio import SeqIO

try:
    SeqIO.convert(sys.stdin, "genbank", sys.stdout, "fasta")
except socket.error as e:
    exit(0)
