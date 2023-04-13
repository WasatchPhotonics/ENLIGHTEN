import logging

log = logging.getLogger(__name__)

class Clipboard(object):
    """
    This class encapsulates access to the host OS (Windows) copy-paste clipboard, 
    allowing tabular data to be copied from ENLIGHTEN and pasted into other 
    applications like Microsoft Excel.
    
    This is NOT related to the "Measurement Capture Bar" along the left-hand
    edge of ENLIGHTEN's GUI, although we seem to be converging toward calling that
    "the ENLIGHTEN Clipboard."
    """
    def __init__(self, clipboard, marquee):
        self.clipboard = clipboard
        self.marquee   = marquee

    def copy_spectra(self, spectra):
        """
        Copies the passed list-of-lists to the clipboard as column-ordered tab-
        delimited lines.
        
        @param spectra   an array of arrays (e.g. [ [wavelengths], [spectrum], [trace_1], [trace_2] ] )
        """
        if spectra is None or len(spectra) == 0:
            return

        # find length of the longest spectrum
        rows = max(len(spectrum) for spectrum in spectra)

        s = ""
        for row in range(rows):
            values = []
            for spectrum in spectra:
                if spectrum is not None:
                    if row < len(spectrum):
                        values.append("%.5f" % spectrum[row])
                    else:
                        values.append("")

            s += "\t".join(values) + "\n" 
            
        self.clipboard.setText(s)
        self.marquee.info("copied %d rows to clipboard" % rows)

    def copy_dict(self, d):
        log.debug("Clipboard.copy_dict called with %s", d)
        s = ""
        rows = 0
        for key in sorted(d):
            s += "%s\t%s\n" % (key, d[key])
            rows += 1
        self.clipboard.setText(s)
        self.marquee.info("copied %d rows to clipboard" % rows)

    def copy_table_widget(self, table):
        """
        Copies the contents of a QTableWidget to the clipboard as tab-delimited lines.
        
        If a rectangular block (presumably one or more contiguous rows or columns) were
        selected in the GUI, then only the selected block is copied.
        
        @see https://stackoverflow.com/a/3698704
        """
        try:
            indices = table.selectedIndexes()
            if len(indices) == 0:
                # copy whole table
                new_table = [[""] * table.columnCount() for i in range(table.rowCount())] 
                rows = table.rowCount()
                cols = table.columnCount()
                for col in range(cols):
                    for row in range(rows):
                        item = table.item(row, col)
                        if item is not None:
                            new_table[row][col] = item.text()
                tab_delimited = "\n".join(("\t".join(i) for i in new_table))
            else:
                # copy selected cells
                cols = indices[-1].column() - indices[0].column() + 1
                rows = len(indices) / cols
                new_table = [[""] * cols for i in range(rows)] 
                for i, index in enumerate(indices):
                    item = table.item(index.row(), index.column())
                    if item is not None:
                        new_table[i % rows][i / rows] = item.text()
                tab_delimited = "\n".join(("\t".join(i) for i in new_table))

            self.clipboard.setText(tab_delimited)
            self.marquee.info("copied %d rows to clipboard" % rows)
        except:
            log.error("error copying table", exc_info=1)

    def raw_set_text(self, text):
        self.clipboard.setText(text)
