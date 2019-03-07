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


DATA_TABLE_NAME = "mash_sketches"

def run(args, cwd):
    proc = subprocess.Popen(args=args, shell=False, cwd=cwd)
    return_code = proc.wait()
    if return_code:
        print("Error building sketch.", file=sys.stderr)
        sys.exit( return_code )

def mash_build_sketch_refseq(data_manager_dict, sketch_type, target_directory, data_table_name=DATA_TABLE_NAME):
    
    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")
    
    database_value = "_".join([
        now,
        "refseq" + "." +
        sketch_type + "." +
        "k21.s1000.msh",
    ])

    database_name = " ".join([
        "refseq" + "." +
        sketch_type + "." +
        "k21.s1000.msh"
        "(Created:",
        now + ")"
    ])

    database_path = database_value
    
    args = [
        'https://gembox.cbcb.umd.edu/mash/refseq.' + sketch_type + '.k21s1000.msh'
    ]

    run(['wget'] + args, target_directory)

    data_table_entry = {
        "value": database_value,
        "name": database_name,
        "path": database_path,
    }
    
    _add_data_table_entry(data_manager_dict, data_table_entry)


def _add_data_table_entry(data_manager_dict, data_table_entry, data_table_name=DATA_TABLE_NAME):
    data_manager_dict['data_tables'] = data_manager_dict.get( 'data_tables', {} )
    data_manager_dict['data_tables'][data_table_name] = data_manager_dict['data_tables'].get( data_table_name, [] )
    data_manager_dict['data_tables'][data_table_name].append( data_table_entry )
    return data_manager_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('data_manager_json')
    parser.add_argument('--sketch-type', dest='sketch_type', help='Sketch Type (genome or plasmid or genome+plasmid)' )
    parser.add_argument( '-t', '--threads', dest='threads', default=1, help='threads' )

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
    
    mash_build_sketch_refseq(
        data_manager_output,
        args.sketch_type,
        target_directory,
    )

    open(args.data_manager_json, 'wb').write(json.dumps(data_manager_output))


if __name__ == "__main__":
    main()
