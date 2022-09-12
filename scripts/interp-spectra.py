import numpy as np
import argparse
import copy
import sys

"""
Interpolates and merges a list of columnar CSV files like this:

    ENLIGHTEN Version,1.5.7
    Measurement ID,20190325-183349-273000-AP15-004
    Serial Number,AP15-004
    Integration Time,2000
    Timestamp,2019-03-25 18:33:49.273000
    Note,
    Temperature,9.9767782325805
    CCD C0,777.2802124023438
    CCD C1,0.2222045361995697
    CCD C2,1.160000010713702e-05
    CCD C3,-3.7399999541776197e-08
    CCD Offset,0
    CCD Gain,1.9
    Laser Wavelength,785
    Laser Enable,False
    Laser Power,100
    Laser Temperature,32.9604622519218
    Pixel Count,1024

    Pixel,Wavelength,Wavenumber,Processed,Raw,Dark,Reference
    0,777.28,-126.52,1082.00,1082.00,,
    1,777.50,-122.84,1065.80,1065.80,,
"""

def warn(msg):
    sys.stderr.write(msg + "\n")

class Record:
    def __init__(self, filename, args=None):
        self.metadata = {}
        self.spectra  = {} # keyed on 'headers'
        self.headers  = []

        with open(filename) as f:
            state = "metadata"
            for line in f:
                line = line.strip()
                if state == "metadata":
                    if len(line) == 0:
                        state = "headers"
                    else:
                        values = line.split(",")
                        if len(values) != 2:
                            raise Exception("can't parse metadata: %s", line)
                        (key, value) = line.split(",")
                        self.metadata[key] = value
                elif state == "headers":
                    if len(line) > 0:
                        self.headers = line.split(",")
                        for header in self.headers:
                            self.spectra[header] = []
                        state = "spectra"
                elif state == "spectra":
                    values = line.split(",")
                    for header in self.headers:
                        value = values.pop(0)
                        if len(value) > 0:
                            value = float(value)
                        else:
                            value = 0
                        self.spectra[header].append(value)

        if args is not None:
            if args.interp_field in self.headers:
                key = f"min_{args.interp_field}"
                value = min(self.spectra[args.interp_field])
                s = f"{value:0.2f}"
                self.metadata[key] = s
                warn(f"{key} = {s}")

                key = f"max_{args.interp_field}"
                value = max(self.spectra[args.interp_field])
                s = f"{value:0.2f}"
                self.metadata[key] = s
                warn(f"{key} = {s}")

def interpolate(m, args, x):
    if args.interp_field not in m.headers:
        # e.g., trying to interpolate on "wavenumber" but a particular CSV didn't have "wavenumber" column
        return -1

    best_y_header = None
    for header in ["Processed", "Spectrum", "Raw"]:
        if header in m.headers:
            best_y_header = header 
            break
    if best_y_header is None:
        return -2
    
    old_x = m.spectra[args.interp_field]
    old_y = m.spectra[best_y_header]
    new_y = np.interp(x, old_x, old_y)
    return new_y

parser = argparse.ArgumentParser(description="acquire from specified device, display line graph")
parser.add_argument("--interp-start", type=float, default=200, help="x-axis start")
parser.add_argument("--interp-stop", type=float, default=2400, help="x-axis stop")
parser.add_argument("--interp-incr", type=float, default=1, help="x-axis increment")
parser.add_argument("--interp-field", type=str, default="Wavenumber", help="x-axis field")
parser.add_argument("--key", type=str, help="metadata field to use as merged column header (filename by default)")
parser.add_argument('filenames', nargs=argparse.REMAINDER)
args = parser.parse_args(sys.argv[1:])

# validate input arguments
warn(f"read {len(args.filenames)} filenames")

# load all files into a dict of Records
data = {}
for filename in args.filenames:
    rec = Record(filename, args)

    if args.key is None:
        key = filename
    else:
        key = rec.metadata[args.key]

    if key in data:
        warn(f"ignoring duplicate key {args.key}: {key}")
    else:
        data[key] = rec
warn(f"read {len(data)} records")

# generate union of all metadata keys (tells us what metadata rows we'll need to output for each spectrometer)
metadata_keys = set()
for key in data:
    for k in data[key].metadata:
        metadata_keys.add(k)
warn(f"found {len(metadata_keys)} unique file keys")

# PREPARE header row for the merged file 
# (need to do this before outputting metadata, so we know how many header fields to skip)
all_headers = [ args.interp_field ]
for key in sorted(data):
    all_headers.append(key)
warn(f"generated {len(all_headers)} headers: {all_headers}")

# OUTPUT metadata 
for meta_key in sorted(metadata_keys):  # output every metadata row
    print(meta_key, end='')             # output metadata key
    for file_key in sorted(data):       # repeat value for each data column
        print(", " + data[file_key].metadata[meta_key], end='')
    print("")
print("")

# OUTPUT header row
print((", ".join(all_headers)))

# output spectra for all records in columns under file keys
row = 0
while True:
    x = args.interp_start + row * args.interp_incr
    if x > args.interp_stop:
        break

    warn(f"starting row {row}, x = {x}")
    values = [ f"{x:0.2f}" ]

    # generate this row's data for each loaded file
    for file_key in sorted(data):
        value = interpolate(data[file_key], args, x)
        values.append(f"{value:0.2f}")

    # output this row's merged data
    print((", ".join(values)))
    row += 1
