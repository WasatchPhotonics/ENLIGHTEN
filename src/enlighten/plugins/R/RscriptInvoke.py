import os
import time
import logging

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class RscriptInvoke(EnlightenPluginBase):
    """
    THIS NEEDS RE-DONE USING RPY2!

    @see https://medium.com/analytics-vidhya/calling-r-from-python-magic-of-rpy2-d8cbbf991571
    """

    def get_configuration(self):
        self.name = "Invoke R"
        self.streaming = False
        self.has_other_graph = True
        self.field(name="Rscript", datatype="string", direction="input")
        self.field(name="File Response", direction="output")

    def process_request(self, request):
        r_script_path = request.plugin_fields["Rscript"]
        output_file = os.path.join(r_script_path, "spectrum_output.csv")

        script_response_file = os.path.join(r_script_path, "analysis_return.csv")

        if os.path.isfile(script_response_file):
            os.remove(script_response_file)

        pr = request.processed_reading
        spectrum = pr.get_processed().tolist()
        wavelengths = pr.get_wavelengths()
        wavenumbers = pr.get_wavenumbers()

        if spectrum is not None:
            spectrum = [str(val) for val in spectrum]

        if wavenumbers is not None:
            wavenumbers = [str(val) for val in wavenumbers]
        else:
            wavenumbers = [str(1000/i) for i in wavelengths]

        if wavelengths is not None:
            wavelengths = [str(val) for val in wavelengths]
        else:
            wavelengths = [0 for _ in spectrum]

        with open(output_file,'w') as csv_file:
            csv_file.write('wavelength, wavenumber, processed\n')
            for i in range(len(spectrum)):
                csv_file.write(f"{wavelengths[i]}, {wavenumbers[i]}, {spectrum[i]}\n")

        os.chdir(r_script_path)
        cmd = f"\"C:\\Program Files\\R\\R-4.0.5\\bin\\Rscript.exe\" {r_script_path}\\RtestScript.R"
        log.debug(f"running: {cmd}")
        os.system(cmd)

        log.debug(f"waiting for {script_response_file}")
        while not os.path.isfile(script_response_file):
            time.sleep(1)
        
        file_res = None
        with open(script_response_file, "r") as read_file:
            file_res = read_file.read()

        # should we delete response file now?

        self.outputs["File Response"] = file_res
