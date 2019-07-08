#!/usr/bin/env python

from __future__ import print_function

import argparse
import datetime
import errno
import glob
import json
import os
import shutil
import string
import subprocess
import sys
import time
import uuid


DATA_TABLE_NAME = "mob_suite_databases"


def mob_suite_build_database_mob_cluster(target_directory, mob_cluster_args, database_name, data_table_name=DATA_TABLE_NAME):

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")

    database_value = str(uuid.uuid1())

    database_name = database_name

    database_path = database_value

    mob_init_args_list = [
        '-d', database_path,
    ]

    subprocess.check_call(['mob_init'] + mob_init_args_list, cwd=target_directory)

    try:
        os.remove(os.path.join(database_path, "clusters.txt"))
    except OSError as e:  ## if failed, report it back to the user ##
        print ("Error: %s - %s." % (e.filename, e.strerror))

    
    ncbi_plasmid_db_files = glob.glob(os.path.join(database_path, "ncbi_plasmid_full_seqs.*"))
    for ncbi_plasmid_db_file in ncbi_plasmid_db_files:
        try:
            os.remove(ncbi_plasmid_db_file)
        except OSError as e:
            print ("Error: %s - %s." % (e.filename, e.strerror))

    
    
    mob_cluster_args_list = [
        '--num_threads', mob_cluster_args['num_threads'],
        '--infile', mob_cluster_args['infile'],
        '--outdir', database_path,
        '--mode', mob_cluster_args['mode'],
    ]
    
    print(json.dumps(mob_cluster_args_list))

    print("Sleeping for 20s")
    time.sleep(20)
    print("Sleep ending")
    
    subprocess.check_call(['mob_cluster'] + mob_cluster_args_list, cwd=target_directory)

    print("Sleeping for 20s")
    time.sleep(20)
    print("Sleep ending")

    shutil.move(os.path.join(target_directory, database_path, 'references_updated.fasta'),
                os.path.join(target_directory, database_path, 'ncbi_plasmid_full_seqs.fas'))
    
    makeblastdb_args_list = [
        '-in', os.path.join(database_path, 'ncbi_plasmid_full_seqs.fas'),
        '-dbtype', 'nucl',
    ]
    
    subprocess.check_call(['makeblastdb'] + makeblastdb_args_list, cwd=target_directory)

    mash_sketch_args_list = [
        '-i', os.path.join(database_path, 'ncbi_plasmid_full_seqs.fas'),
    ]

    subprocess.check_call(['mash', 'sketch'] + mash_sketch_args_list, cwd=target_directory)

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
                    "path": os.path.join(database_path, 'data')
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
