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


DATA_TABLE_NAME = "mob_suite_databases"


def mob_suite_build_database_mob_init(mob_suite_args, target_directory, data_table_name=DATA_TABLE_NAME):

    now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H%M%SZ")

    database_value = "_".join([
    ])

    database_name = " ".join([
    ])

    database_path = database_value

    args = [
    ]

    run(['mob_init'] + args, target_directory)

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
    parser.add_argument( '--threads', dest='threads', default=1, help='threads' )
    parser.add_argument( '--mode', dest='mode', default=1, help='database construction mode' )
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

    if str(args.mode) == 'mob_init':
        mob_suite_args = {}
        data_manager_output = mob_suite_build_database_mob_init(
            mob_suite_args,
            target_directory,
        )
    else:
        sys.exit("Invalid database construction mode")

    open(args.data_manager_json, 'wb').write(json.dumps(data_manager_output))


if __name__ == "__main__":
    main()
