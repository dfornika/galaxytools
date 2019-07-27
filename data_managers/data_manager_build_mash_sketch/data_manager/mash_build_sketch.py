#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime
import errno
import json
import os
import shutil
import string
import subprocess
import sys
import uuid


DATA_TABLE_NAME = "mash_sketches"


def mash_build_sketch(target_directory, mash_args, database_name, data_table_name=DATA_TABLE_NAME):

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")

    database_value = str(uuid.uuid4())

    database_name = database_name

    database_path = database_value

    try:
        os.mkdir( os.path.join(target_directory, database_path) )
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir( os.path.join(target_directory, database_path) ):
            pass
        else:
            raise

    shutil.copyfile(mash_args['input'], os.path.join(target_directory, database_path, 'seqs.fasta'))
          
    mash_sketch_args_list = [
        '-p', mash_args['threads'],
        '-k', mash_args['kmer_size'],
        '-s', mash_args['sketch_size'],
        '-i', 'seqs.fasta',
        '-o', 'sketch',
    ]

    subprocess.check_call(['mash', 'sketch'] + mash_sketch_args_list,
                          cwd=os.path.join(target_directory, database_path))
    
    bagit_args_list = [
        database_path,
    ]

    subprocess.call(['bagit.py'] + bagit_args_list, cwd=target_directory)
    
    data_table_entry = {
        "data_tables": {
            data_table_name: [
                {
                    "value": database_value,
                    "name": database_name,
                    "path": os.path.join(database_path, 'data'),
                }
            ]
        }
    }

    return data_table_entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_manager_json')
    parser.add_argument('--threads', dest='threads', default=1, help='threads' )
    parser.add_argument('--input', dest='input', help='Plasmid Assemblies (.fasta)')
    parser.add_argument('--kmer-size', dest='kmer_size', help='K-mer size' )
    parser.add_argument('--sketch-size', dest='sketch_size', help='Sketch size' )
    parser.add_argument('--database-name', dest='database_name', help='Database Name')
    args = parser.parse_args()

    data_manager_input = json.loads(open(args.data_manager_json).read())

    target_directory = data_manager_input['output_data'][0]['extra_files_path']

    mash_args = {
        'input': args.input,
        'kmer_size': args.kmer_size,
        'sketch_size': args.kmer_size,
        'threads': args.threads,
    }

    try:
        os.mkdir( target_directory )
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir( target_directory ):
            pass
        else:
            raise

    data_manager_output = {}

    data_manager_output = mash_build_sketch(
        target_directory,
        mash_args,
        args.database_name,
    )

    open(args.data_manager_json, 'wb').write(json.dumps(data_manager_output))


if __name__ == "__main__":
    main()
