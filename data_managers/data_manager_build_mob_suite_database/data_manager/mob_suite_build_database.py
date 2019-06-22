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
import uuid


DATA_TABLE_NAME = "mob_suite_databases"


def mob_suite_build_database_mob_cluster(target_directory, mob_cluster_args, database_name, data_table_name=DATA_TABLE_NAME):

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")

    database_value = str(uuid.uuid4())

    database_name = database_name

    database_path = database_value

    args = [
        '--num_threads', mob_cluster_args['num_threads'],
        '--infile', mob_cluster_args['infile'],
        '--outdir', database_path,
        '--mode', mob_cluster_args['mode'],
    ]

    subprocess.check_call(['mob_cluster'] + args, cwd=target_directory)

    data_table_entry = {
        "data_tables": {
            data_table_name: [
                {
                    "value": database_value,
                    "name": database_name,
                    "path": database_path,
                }
            ]
        }
    }

    return data_table_entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_manager_json')
    parser.add_argument('--threads', dest='threads', default=1, help='threads')
    parser.add_argument('--input', dest='input', help='Plasmid Assemblies (.fasta)')
    parser.add_argument('--database-name', dest='database_name', help='Database Name')
    args = parser.parse_args()

    data_manager_input = json.loads(open(args.data_manager_json).read())

    target_directory = data_manager_input['output_data'][0]['extra_files_path']

    try:
        os.mkdir( target_directory )
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir( target_directory ):
            pass
        else:
            raise

    data_manager_output = {}

    mob_cluster_args = {
        'num_threads': args.threads,
        'infile': args.input,
        'mode': 'build',
    }
    
    data_manager_output = mob_suite_build_database_mob_cluster(
        target_directory,
        mob_cluster_args,
        args.database_name,
    )


    open(args.data_manager_json, 'wb').write(json.dumps(data_manager_output))


if __name__ == "__main__":
    main()
