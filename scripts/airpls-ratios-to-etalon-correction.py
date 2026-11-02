import json
import argparse

class Converter:
    """
    Converts list of AirPLS ratios into an ENLIGHTEN-compatible JSON config file of the inverted factors.
    """
    def __init__(self):
        parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("--infile", type=str, required=True, help="file of AirPLS ratios, one float per line")
        parser.add_argument("--outfile", type=str, required=True, help="new JSON file to create")
        parser.add_argument("--roi-start", type=int, help="start of horizontal ROI", default=0)
        parser.add_argument("--pixels", type=int, help="number of pixels", default=1952)
        self.args = parser.parse_args()

    def run(self):
        factors = []

        # pad up to ROI start
        if self.args.roi_start > 0:
            for pixel in range(self.args.roi_start):
                factors.append(1.0)

        # load ratios, inverting as we go
        with open(self.args.infile) as infile:
            count = 0
            for line in infile:
                ratio = float(line)
                factors.append(1.0 / ratio)
                count += 1
            print(f"read {count} ratios from {self.args.infile}")

        # pad up to pixels 
        while len(factors) < self.args.pixels:
            factors.append(1.0)

        print(f"ready to write {len(factors)} factors to {self.args.outfile}")
        data = {
            "pixel_corrections": {
                "etalon_correction": {
                    "mode": "default",
                    "factors": factors
                }
            }
        }
        with open(self.args.outfile, "w") as outfile:
            json.dump(data, outfile, indent=4, sort_keys=True)
        print("done")
        
if __name__ == "__main__":
    converter = Converter()
    converter.run()
