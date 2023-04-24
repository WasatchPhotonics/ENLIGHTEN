import argparse
import csv
import sys
import os

"""
Transposes one or more input CSV files into a single concatenated, transposed output
with added header rows and header column.

one.csv
    1,  2,  3,  4
    5,  6,  7,  8
    9, 10, 11, 12

two.csv
    a, b, c
    d, e, f  

...into this (whitespace added for legibility):

     ,     one,    one,    one,    two,    two
     ,     one-01, one-02, one-03, two-01, two-02
    0,     1,      5,      9,      a,      d
    1,     2,      6,      10,     b,      e
    2,     3,      7,      11,     c,      f
    3,     4,      8,      12


Invocation: 
    $ python scripts/transpose.py [--mean] one.csv two.csv > ~/transposed.csv
"""

parser = argparse.ArgumentParser(description="Transpose one or more input files from rows to columns")
parser.add_argument("--average", action="store_true", help="average all rows in input file before transposing")
parser.add_argument("filenames", type=str, nargs="+", help="input CSV files to transpose")
(args, filenames) = parser.parse_known_args(sys.argv[1:])

if len(args.filenames) == 0:
    print("Usage: list of filenames")
    sys.exit(1)

# load all files into a dict (keyed on filename)
data = {}
for filename in args.filenames:
    short = os.path.splitext(os.path.basename(filename))[0]
    rows = []
    with open(filename) as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    # perform any pre-processing on each file after loading
    if args.average:
        averaged = []
        cols = len(rows[0])
        for col in range(cols):
            total = 0
            for row in rows:
                total += float(row[col])
            averaged.append(total / len(rows))
        rows = [ averaged ]

    data[short] = rows

# output header rows
header_one = [ "" ]
header_two = [ "" ]
max_cols = 0
for name in data:
    rows = len(data[name])
    cols = len(data[name][0])
    max_cols = max(max_cols, cols)
    for i in range(rows):
        header_one.append(name)
        header_two.append(f"{name}-{i:02d}")
print(", ".join(header_one))
print(", ".join(header_two))

# output transposed data
for col in range(max_cols):
    values = [ str(col) ]
    for name in data:
        rows = len(data[name])
        cols = len(data[name][0])
        for row in range(rows):
            value = ""
            if col < cols:
                value = data[name][row][col]
            values.append(str(value).strip())
    print(", ".join(values))
