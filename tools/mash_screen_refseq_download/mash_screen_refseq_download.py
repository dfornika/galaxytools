#!/bin/env python

import csv
import re
import sys
import time
import urllib.request

def parse_mash_result(path_to_mash_screen):
    """
    Args:
        path_to_mash_screen (str): Path to the mash screen report file.
    Returns:
        list(dict): Parsed mash screen report
        For example:
        [
          { "identity": 0.996805,
            "shared_hashes": "935/1000",
            "median_multiplicity": 38,
            "p_value": 0.00,
            "query_id": "GCF_001022155.1_ASM102215v1_genomic.fna.gz",
            "query_comment": "[10 seqs] NZ_CP011612.1 Citrobacter freundii strain CAV1321, complete genome [...]"
          },
          { "identity": 0.914483,
            ...
          }
        ]
        See mash docs for more info on mash screen report file:
        https://mash.readthedocs.io/en/latest/tutorials.html#screening-a-read-set-for-containment-of-refseq-genomes
    """

    mash_screen_report_fields = {
        'identity': lambda x: float(x),
        'shared_hashes': lambda x: x,
        'median_multiplicity': lambda x: int(x),
        'p_value': lambda x: float(x),
        'query_id': lambda x: x,
        'query_comment': lambda x: x
    }
    
    # Example mash screen report record (actual report has no header and is tab-delimited):
    # identity    shared_hashes    median_multiplicity    p_value    query_id                                    query_comment
    # 0.998697    973/1000         71                     0          GCF_000958965.1_matepair4_genomic.fna.gz    [59 seqs] NZ_LAFU01000001.1 Klebsiella pneumoniae strain CDPH5262 contig000001, whole genome shotgun sequence [...]

    parsed_mash_result = []
    with open(path_to_mash_screen) as mashfile:
        reader = csv.DictReader(mashfile, delimiter='\t', fieldnames=list(mash_screen_report_fields))
        mash_record = {}
        for row in reader:
            for field_name, parse in mash_screen_report_fields.items():
                mash_record[field_name] = parse(row[field_name])
            parsed_mash_result.append(mash_record.copy())
    return parsed_mash_result

def mash_query_id_to_ncbi_ftp_path(query_id):
        """
        Args:
            query_id (str): Mash query ID (column 5 of mash screen report)
        Returns:
            list: Directory names used to locate reference genome
                  on ftp://ftp.ncbi.nlm.nih.gov/genomes/all/
        For example:
            "GCF/001/022/155"
        """
        prefix = query_id.split('_')[0]
        digits = query_id.split('_')[1].split('.')[0]
        path_list = [prefix] + [digits[i:i+3] for i in range(0, len(digits), 3)]

        return "/".join(path_list)

def main():

    mash_results = parse_mash_result(sys.argv[1])

    for mash_result in mash_results:
        url = None
        query_id = mash_result['query_id']
        if re.match("^ref\|", query_id):
            accession = re.search('ref\|(.*)\|', mash_result['query_id']).group(1)
            url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?" + \
            "&".join([
                "db=nucleotide",
                "id=" + accession,
                "rettype=fasta",
            ])
            # NCBI API is rate-limited to 3 requests per second, so pause between requests
            time.sleep(1)
            urllib.request.urlretrieve(url, accession + ".fasta")
        elif re.match("^GCF", query_id):
            ncbi_ftp_path = mash_query_id_to_ncbi_ftp_path(query_id)
            assembly = query_id[:query_id.find("_genomic.fna.gz")]
            ncbi_ftp_server_base = "ftp://ftp.ncbi.nlm.nih.gov"
            url = "/".join([
                ncbi_ftp_server_base, "genomes", "all",
                ncbi_ftp_path,
                assembly,
                query_id
            ])
            # NCBI API is rate-limited to 3 requests per second, so pause between requests
            time.sleep(1)
            urllib.request.urlretrieve(url, query_id)
        else:
            print("query ID: " + mash_result['query_id'] + " not recognized.")

    
if __name__ == '__main__':
    main()
