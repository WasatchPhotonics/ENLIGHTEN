import logging

log = logging.getLogger(__name__)

## Static product information about standard spectrometer models
#   Product          MeanAvgRes MaxAvgRes MeanMaxRes MaxRes
TABLE = """
    WP-785-SR-A-50      9.4        9.6       10.8       11.0
    WP-785-SR-R-25      5.4        6.2       6.3        7.2
    WP-785-SR-R-50      9.5        9.9       11.0       11.7
    WP-785-SR-C-10      4.3        5         4.9        6.3
    WP-785-SR-C-25      5.6        6.1       6.5        7.4
    WP-785-SR-C-50      9.6        10.2      11.3       12.1
    WP-785-ER-C2-10     6.2        6.7       8.1        8.9
    WP-785-ER-C2-25     7.8        8.7       9.5        11.7
    WP-785-ER-C2-50     13.4       13.4      15.8       15.8
    WP-785-ER-C2-100    21.6       21.6      26.8       26.8
    WP-785-ER-R2-10     7.3        7.5       9.4        10.1
    WP-785-ER-R2-25     6.9        7.1       8.4        9.7
    WP-785-A-25-OEM     7.2        7.2       9          9
    WP-785-A-50-OEM     13.4       13.5      15.4       15.4
    WP-785-R-25-OEM     7.2        7.7       8.4        9.1
    WP-785-R-50-OEM     13.0       13.6      14.6       15.6
    WP-785-C-25-OEM     8          8         13.16      13.16
    WP-785-C-50-OEM     12.7       12.7      14.0       14.1
    WP-830-SR-R-10      4.1        4.1       5.2        5.2
    WP-830-SR-R-25      5.8        6.1       6.9        7.0
    WP-830-SR-R-50      9.5        10.3      11.3       12.9
    WP-830-SR-C-50      9.7        10.3      11.4       13.0
    WP-1064-ER-C-25-OEM 7.5        7.9       10.7       11.9
    WP-1064-ER-C-50-OEM 13.4       13.4      16.4       16.4
    WP-1064-SR-C-25     5.2        5.4       6.9        7.8
    WP-1064-SR-C-50     9.9        10.5      11.4       12.3
    WP-532-SR-A-50      14.7       14.7      16.8       16.8
    WP-532-ER-C-10-UCL  6.0        6         7.0        7.0
    WP-532-ER-C-25-UCL  6.7        7.5       8.8        10.2
    WP-532-ER-C-50-UCL  9.8        9.8       10.9       10.9
    WP-532-ER-C-10      8.4        10.9      11.4       14.1
    WP-532-ER-C-25      10.3       12.9      12.6       17.1
    WP-532-ER-C-50      19.9       21.2      24.0       24.3
    WP-532-SR-C-10      7.2        8.1       7.8        8.4
    WP-532-SR-C-25      8.1        8.5       10.5       12
    WP-532-ER2-C-25     6.9        6.9       7.5        7.5
    WP-532-ER-R-25      13.4       13.4      13.9       13.9
    WP-532-ER-R-50      22.8       22.8      23.2       23.2
    WP-532-SR-R-10      7.4        7.5       9.2        10.2
    WP-532-SR-R-50      14.2       15        16.4       17.3
    WP-532-XSR-R-25     7.9        7.9       11.8       11.8
    WP-633-SR-R-10      4.3        4.3       5.3        5.3
    WP-633-SR-R-25      7.0        7         8.3        8.8
    WP-633-SR-R-50      11.7       12.1      13.8       14.2
    WP-633-ER-R-10      4.9        4.9       5.6        5.6
    WP-633-ER-R-25      6.7        7         7.8        8.1
    WP-633-ER-R-50      11.8       11.8      13.5       13.5
"""

class ModelFWHM(object):

    def __init__(self):
        self._parse_table()

    def _parse_table(self):
        self.table = {}

        for line in TABLE.splitlines():
            line = line.strip()
            if len(line) == 0:
                continue
            tok = line.split()
            if len(tok) < 2:
                log.debug("parse_table: ignoring: %s", line)
                continue

            model = tok[0].upper()
            avg   = float(tok[1])

            self.table[model] = avg

    def get_by_model(self, full_model):

        # look for exact-match
        if full_model in self.table:
            fwhm = self.table[full_model]
            log.debug("perfect match: %s -> %f", full_model, fwhm)
            return fwhm

        # look for key in full_model
        for key in self.table:
            if key in full_model:
                fwhm = self.table[key]
                log.debug("partial match: %s (%s) -> %f", full_model, key, fwhm)
                return fwhm

        # split full_model and keys on hyphenated tokens, and return if all match
        model_tok = set()
        for tok in full_model.split("-"):
            model_tok.add(tok.upper())

        for key in self.table:
            key_tok = key.split("-")
            matched_all = True
            for tok in key_tok:
                if tok not in model_tok:
                    matched_all = False
                    break
            if matched_all:
                fwhm = self.table[key]
                log.debug(f"scrambled match: {full_model} ({key}) -> {fwhm}")
                return fwhm

        log.error(f"could not find model {full_model} in FWHM table")
