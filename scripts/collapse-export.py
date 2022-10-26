#!/usr/bin/env python

import re
import sys
import argparse

parser = argparse.ArgumentParser(description="reduce the number of columns in an Export file")
parser.add_argument("--exclude-field", type=str, help="check this field when applying the exclude-pattern")
parser.add_argument("--exclude-pattern", type=str, help="EXCLUDE columns where 'field' matches this pattern")
parser.add_argument("--infile", type=str, help="file to process")
args = parser.parse_args(sys.argv[1:])

exclude_cols = []
rows = []

with open(args.infile) as infile:
    for line in infile:
        values = [ x.strip() for x in line.split(",") ]
        rows.append(values)
        
        if values[0].lower() == args.exclude_field.lower():
            for i in range(len(values)):
                if re.match(args.exclude_pattern, values[i], re.IGNORECASE):
                    exclude_cols.append(i)

for row in rows:
    good_cols = []
    for i in range(len(row)):
        if i not in exclude_cols:
            good_cols.append(row[i])
    print(", ".join(good_cols))
