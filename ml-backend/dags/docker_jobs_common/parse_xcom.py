#!/usr/bin/env python
"""
Helper to parse XCOM data
See https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/xcoms.html#xcoms
and LazySelectSequence in
https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/dynamic-task-mapping.html
"""
__author__ = "Thomas Ranzenberger"
__copyright__ = "Copyright 2022, Technische Hochschule Nuernberg"
__license__ = "Apache 2.0"
__version__ = "1.0.0"
__status__ = "Draft"


import argparse
import ast
import sys


parser = argparse.ArgumentParser(description="Helper to parse XCOM data")
parser.add_argument("data", type=str, help="XCOM data string")
parser.add_argument(
    "keys",
    type=str,
    help="Key or mulitple comma seperated keys in the XCOM data string, value of first key which is found will be returned",
)
args = parser.parse_args()

search_array = []

if "," in args.keys:
    search_array = args.keys.split(",")
else:
    search_array.append(args.keys)

try:
    xcom_array = ast.literal_eval(args.data)
    for item in xcom_array:
        for search_key in search_array:
            if search_key in item:
                if isinstance(item, dict):
                    data = item[search_key]
                    print(data)
                    sys.exit(0)
                else:
                    data = xcom_array[search_key]
                    print(data)
                    sys.exit(0)
        xcom_dict = dict(item)
        for subitem in xcom_dict:
            for search_key in search_array:
                if search_key in subitem:
                    data = subitem[search_key]
                    print(data)
                    sys.exit(0)
    print("")
    sys.exit(0)
except:
    sys.exit(-1)
