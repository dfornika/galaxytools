#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime
import errno
import json
import os
import string
import subprocess
import sys

from pprint import pprint

DATA_TABLE_NAME = "kraken2_databases"

def kraken2_build_standard(data_manager_dict, kraken2_args, params, target_directory, data_table_name=DATA_TABLE_NAME):
    today = datetime.date.today().isoformat()
    database_name = "_".join([today, "standard"])
    args = [
        'kraken2-build',
        '--threads', str(kraken2_args["threads"]),
        '--standard',
        '--kmer-len', str(kraken2_args["kmer_len"]),
        '--minimizer-len', str(kraken2_args["minimizer_len"]),
        '--minimizer-spaces', str(kraken2_args["minimizer_spaces"]),
        '--db', database_name
    ]
    proc = subprocess.Popen(args=args, shell=False, cwd=target_directory)
    return_code = proc.wait()
    if return_code:
        print("Error building database.", file=sys.stderr)
        sys.exit( return_code )
    args = [
        'kraken2-build',
        '--threads', str(kraken2_args["threads"]),
        '--clean',
        '--db', database_name
    ]
    proc = subprocess.Popen(args=args, shell=False, cwd=target_directory)
    return_code = proc.wait()
    if return_code:
        print("Error building database.", file=sys.stderr)
        sys.exit( return_code )
    data_table_entry = {
        "value": database_name,
        "name": database_name,
        "path": database_name
    }
    
    _add_data_table_entry(data_manager_dict, data_table_name, data_table_entry)


def _add_data_table_entry(data_manager_dict, data_table_name, data_table_entry):
    data_manager_dict['data_tables'] = data_manager_dict.get( 'data_tables', {} )
    data_manager_dict['data_tables'][ data_table_name ] = data_manager_dict['data_tables'].get( data_table_name, [] )
    data_manager_dict['data_tables'][ data_table_name ].append( data_table_entry )
    return data_manager_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('params')
    parser.add_argument( '-k', '--kmer-len', dest='kmer_len', type=int, default=35, help='kmer length' )
    parser.add_argument( '-m', '--minimizer-len', dest='minimizer_len', type=int, default=31, help='minimizer length' )
    parser.add_argument( '-s', '--minimizer-spaces', dest='minimizer_spaces', default=6, help='minimizer spaces' )
    parser.add_argument( '-t', '--threads', dest='threads', default=1, help='threads' )
    args = parser.parse_args()

    kraken2_args = {
        "kmer_len": args.kmer_len,
        "minimizer_len": args.minimizer_len,
        "minimizer_spaces": args.minimizer_spaces,
        "threads": args.threads,
    }
    
    params = json.loads(open(args.params).read())
    pprint(params)
    target_directory = params['output_data'][0]['extra_files_path']

    try:
        os.mkdir( target_directory )
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir( target_directory ):
            pass
        else:
            raise

    data_manager_dict = {}

    # build the index
    kraken2_build_standard(
        data_manager_dict,
        kraken2_args,
        params,
        target_directory
    )

    # save info to json file
    open(args.params, 'wb').write(json.dumps(data_manager_dict))


if __name__ == "__main__":
    main()
