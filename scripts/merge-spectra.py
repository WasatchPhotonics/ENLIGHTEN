import copy
import sys

"""
Merges columnar CSV's like this, keyed on Timestamp:

    Integration Time,1500
    Timestamp,2019-03-22 22_44_02.437000
    Note,note
    Temperature,10.01
    CCD C0,770.111328125
    CCD C1,0.22512559592723846
    CCD C2,9.989999853132758e-06
    CCD C3,-3.5700001177474405e-08
    CCD Offset,0
    CCD Gain,1.9
    Laser Wavelength,785.0
    Laser Enable,False
    Laser Power,100
    Laser Temperature,31.10
    Pixel Count,1024

    Pixel,Wavelength,Spectrum
    0,770.11,980.80
    1,770.34,973.40

or...

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

class Record:
    def __init__(self, filename):
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
                        self.spectra[header].append(values.pop(0))

# validate input arguments
filenames = sys.argv[1:]
if len(filenames) == 0:
    print("Usage: list of filenames")
    sys.exit(1)

# load all files into a dict of Records
data = {}
for filename in filenames:
    rec = Record(filename)
    timestamp = rec.metadata["Timestamp"]
    data[timestamp] = rec

# generate list of metadata keys
metadata_keys = set()
first_timestamp = None
for timestamp in sorted(data):
    for key in data[timestamp].metadata:
        metadata_keys.add(key)
    if first_timestamp is None:
        first_timestamp = timestamp

# PREPARE header row for the merged file 
# (need to do this before outputting metadata, so we know how many header fields to skip)
prefix_headers = []
for header in data[first_timestamp].headers:
    if header not in ["Spectrum", "Processed", "Raw", "Dark", "Reference"]:
        prefix_headers.append(header) 
all_headers = copy.copy(prefix_headers)
for timestamp in sorted(data):
    all_headers.append(data[timestamp].metadata["Timestamp"])

# OUTPUT metadata 
for key in sorted(metadata_keys):
    print(key, end='')                          # atop first prefix header
    for i in range(len(prefix_headers) - 1):    # skip remaining prefix headers
        print(', ', end='')
    for timestamp in sorted(data):              # repeat value for each data column
        print(', %s' % data[timestamp].metadata[key], end='')
    print('')
print("")

# OUTPUT header row
print((",".join(all_headers)))

# output spectra for all records in columns under timestamp headers
for i in range(len(data[first_timestamp].spectra[prefix_headers[0]])):
    values = []

    # prefix each output row with the pixels, wavelengths etc from first file
    for header in prefix_headers:
        values.append(data[first_timestamp].spectra[header][i])

    # output this pixel's data for each loaded file
    for timestamp in sorted(data):

        # only output a single column from subsequent files...different ENLIGHTEN versions changed column names
        if "Spectrum" in data[timestamp].spectra:
            values.append(data[timestamp].spectra["Spectrum"][i])
        elif "Processed" in data[timestamp].spectra:
            values.append(data[timestamp].spectra["Processed"][i])
        elif "Raw" in data[timestamp].spectra:
            values.append(data[timestamp].spectra["Raw"][i])

    # output this pixel's merged data
    print((",".join(values)))
