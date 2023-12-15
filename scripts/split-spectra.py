#!/usr/bin/env python

# invocation:
# $ export PYTHONPATH=~/work/code/enlighten:~/work/code/Wasatch.PY
# $ conda activate wasatch3
# $ conda install xlwt          # easier to patch wasatch3 than get conda_enlighten3 working on a Mac
# $ python split-spectra.py /path/to/*.csv

import re
import os
import sys
import logging
import argparse

from enlighten.parser.ExportFileParser import ExportFileParser
from wasatch import applog

parser = argparse.ArgumentParser(description="Split 'export' CSV into individual per-measurement CSV files")
parser.add_argument("--integration-time-ms",    type=int,   help="only export meansurements with this integration time")
parser.add_argument("--label",                  type=str,   help="only export spectra matching this label (raw, dark, processed etc)")
parser.add_argument("--out-dir",                type=str,   help="output directory (default .)")
(args, filenames) = parser.parse_known_args(sys.argv[1:])

log = logging.getLogger(__name__)
logger = applog.MainLogger("DEBUG")

label_counts = {}

for filename in filenames:
    print("Processing %s" % filename)

    parser = ExportFileParser(filename)
    measurements = parser.parse()
    print("  %d measurements parsed" % len(measurements))

    for m in measurements:

        label = m.label

        label = re.sub(r'\d{4}[-_]*\d{2}[-_]*\d{2}[-_ ]\d{2}:\d{2}:\d{2}', '', label)
        label = re.sub(r'Spectrum', '', label, re.IGNORECASE)
        label = re.sub("\d+x\d+m?s", "", label) # e.g. 10x100ms
        
        # remove spaces from labels
        label = label.strip()
        label = re.sub(" ", "", label)
        label = re.sub("/", "", label)
        if args.integration_time_ms is not None:
            if args.integration_time_ms != m.settings.state.integration_time_ms:
                print(f"  skipping (integration time {m.settings.state.integration_time_ms} != {args.integration_time_ms}")
                continue

        if args.label is not None:
            if args.label.lower() not in label.lower():
                print(f"  skipping (label {args.label} not in {label})")
                continue

        if label not in label_counts:
            label_counts[label] = 0
        label_counts[label] += 1

        # replace basename with label-NN
        m.basename = "%s-%03d" % (label, label_counts[label])
        if args.out_dir:
            m.basename = os.path.join(args.out_dir, m.basename)

        print("  extracting %s" % m.basename)
        m.save_csv_file_by_column(use_basename=True)

log.info(None)
logger.close()
applog.explicit_log_close()
