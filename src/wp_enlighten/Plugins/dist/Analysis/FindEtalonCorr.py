import os
import json
import logging
import numpy as np

# backward compatibility with ENLIGHTEN prior to 4.3.0
try:
    from wp_enlighten import common
except ModuleNotFoundError as e:
    if e.name != "wp_enlighten":
        raise
    from enlighten import common
    
from superman.baseline import ALS
from scipy.signal import savgol_filter

from EnlightenPlugin import EnlightenPluginBase

log = logging.getLogger(__name__)

class FindEtalonCorr(EnlightenPluginBase):
    """
    Simple plug-in to determine etalon correction from the current (broadband) 
    spectrum. Also adds the corrected spectrum as a second trace to the main 
    graph.
    """

    def get_configuration(self):
        log.debug("Find Etalon Corr Plugin - configuration")

        self.name = "Find Etalon Correction"
        self.correction = None

        self.field(name="Start of Analysis", datatype=float, direction="input", initial=0, minimum=0, maximum=5000,
                tooltip = "Set to lower limit of etalon correction calculation region. Avoid the sharp filter edge")
        self.field(name="End of Analysis", datatype=float, direction="input", initial=0, minimum=0, maximum=5000,
                tooltip = "Set to upper limit of etalon correction calcuation region. Avoid near-zero signals")
        self.field(name="Smoothness", datatype=float, direction="input", initial=5, minimum=2, maximum=8,
                tooltip = "Adjust smoothness of fitted curve. 2 = very flexible, 8 = very stiff. Corrected curve should no longer trace etaloning features")
        self.field(name="Calculate Correction", datatype="button",  callback=self.calculate,
                tooltip = "Click to update the etalon correction calculation with current spectrum and settings")
        self.field(name="Apply Correction", datatype=bool, initial=True, direction="input",
                tooltip = "Check for live display of etalon corrected spectrum for sanity check")
        self.field(name="Save Correction", datatype="button",  callback=self.save,
                tooltip = "Click to save current etalon correction in config folder")

    def process_request(self, request):
        """
        read and save spectrum, x axis, and 'region of analysis'
        add cursor lines to indicate region of analysis
        if 'apply correction' is checked and a correction exists, add corrected spectrum
        """
        pr = request.processed_reading
        self.spectrum = pr.get_processed()
        self.x_axis = self.get_axis(processed_reading=pr)
        self.start = request.fields["Start of Analysis"]
        self.end = request.fields["End of Analysis"]
        self.smooth = pow(10, request.fields["Smoothness"])
        self.serial_number = request.settings.eeprom.serial_number
        self.roi_start = request.settings.eeprom.roi_horizontal_start
        self.roi_end = request.settings.eeprom.roi_horizontal_end
        self.num_pixels = request.settings.eeprom.active_pixels_horizontal
        
        # first run through request - update region of analysis to full range
        if self.start == 0 and self.end == 0:
            self.get_widget_from_name("Start of Analysis").setValue(self.x_axis[0])
            self.get_widget_from_name("End of Analysis").setValue(self.x_axis[-1])
               
        if not (self.start == 0 and self.end == 0): 
            self.plot(title="start", x=[self.start, self.start], y=[min(self.spectrum), max(self.spectrum)])
            self.plot(title="end", x=[self.end, self.end], y=[min(self.spectrum), max(self.spectrum)])
                
        if request.fields["Apply Correction"] and self.correction is not None:
            log.debug(f"Find Etalon Corr Plugin - applying correction")
            corrected = [ self.correction[i] * intensity for i,intensity in enumerate(self.spectrum) ]
            self.plot(title="corrected", y=corrected, x=self.x_axis)

    def calculate(self):
        """
        Calculate a full-detector array of multiplicative etalon correction factors.
        The calculation follows the R workflow:
          1. Use average spectrum provided by Enlighten
          2. Fit baseline to the spectrum.
          3. Set signal/baseline to 1 outside the analysis interval (as defined by user).
          4. Apply a Savitzky-Golay filter to the ratio.
          5. Invert the smoothed ratio to obtain the multiplicative correction.
          6. Keep detector pixels outside the analysis region at 1.0.
        """
        
        if not ((self.start == 0 and self.end == 0) or self.start == self.end): 
            log.debug("Find Etalon Corr Plugin - calculating correction...")
            
            # these are 'inside' the ROI
            self.correction = np.ones(len(self.spectrum), dtype=float)
            start_index = next((i for i, val in enumerate(self.x_axis) if val >= self.start), 0)
            end_index = next((i for i, val in reversed(list(enumerate(self.x_axis))) if val <= self.end), len(self.x_axis))
            analysis_region = np.array(self.spectrum[start_index:(end_index+1)])
            
            baseline_fit = ALS(
                asymmetry_param=0.1, 
                smoothness_param=self.smooth,
                max_iters=10,
                conv_thresh=0.001
            ).fit(
                bands=None,
                intensities=analysis_region
            ).baseline
            
            ratio = analysis_region / baseline_fit
            smooth_ratio = savgol_filter(ratio, window_length=11, polyorder=3)
            
            # overwrite the ones in the analysis region
            self.correction[start_index:(end_index+1)] = 1.0 / smooth_ratio
            log.debug("Find Etalon Corr Plugin - correction calculated")
        else:
            log.debug("Find Etalon Corr Plugin - no calculation: ROI cursors not yet set")
            self.correction = None

    def save(self):
        """ Save factors in Enlighten's pixel_corrections JSON structure. """
        
        if self.correction is not None:
            log.debug("Find Etalon Corr Plugin - saving correction")
            
            # this is for all pixels
            values = np.ones(self.num_pixels, dtype=float)
            values[self.roi_start:(self.roi_end+1)] = np.asarray(self.correction, dtype=float)

            if not np.all(np.isfinite(values)):
                log.debug("Find Etalon Corr Plugin - Correction factors contain NaN or infinite values.")
            else: 
                payload = {
                    "pixel_corrections": {
                        "etalon_correction": {
                            "mode": "default",
                            "factors": values.tolist(),
                        }
                    }
                }
                output_path = os.path.join(common.get_default_data_dir(), "config", f"{self.serial_number}.json")
                
                # Serialize the factors as a single-line list.
                factors_json = json.dumps(values.tolist(), allow_nan=False)

                # Build the JSON while keeping the surrounding structure readable.
                json_text = (
                    '{\n'
                    '  "pixel_corrections": {\n'
                    '    "etalon_correction": {\n'
                    '      "mode": "default",\n'
                    f'      "factors": {factors_json}\n'
                    '    }\n'
                    '  }\n'
                    '}\n'
                )

                with open(output_path, "w", encoding="utf-8") as stream:
                    stream.write(json_text)  
                    
                log.debug("Find Etalon Corr Plugin - correction saved successfully")
                
                # also make Enlighten look for the file
                spec = self.ctl.multispec.current_spectrometer()
                if spec is not None:
                    spec.settings.augment_from_json_file()
                    # and add the button
                    self.ctl.etalon_correction.update_visibility()
                    log.debug("Find Etalon Corr Plugin - correction loaded into Enlighten")
                            
        else:
            log.debug("Find Etalon Corr Plugin - not saving: correction not yet calculated")

    def disconnect(self):
        super().disconnect()
