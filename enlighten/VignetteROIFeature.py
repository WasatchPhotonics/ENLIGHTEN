import logging

log = logging.getLogger(__name__)

##
# Changing how this works from initial implementation.  Dropping the checkbox, 
# and enabling the feature for any spectrometer which has vignetting (ROI Horizontal 
# Start/Stop) defined in its EEPROM.
class VignetteROIFeature(object):
    
    def __init__(self,
            multispec):
        self.multispec = multispec
        self.observers = set()
        self.update_visibility()

    ## provided for RichardsonLucy to flush its Gaussian cache
    def register_observer(self, callback):
        self.observers.add(callback)

    def update_visibility(self):
        spec = self.multispec.current_spectrometer()
        for callback in self.observers:
            callback()

    ##
    # Called by LOTS of classes :-(
    #
    # @param spectrum (Input) Note this is really "array" or "data", as this can 
    #                      be (and often is) used to crop an x-axis of wavelengths 
    #                      or wavenumbers.
    # @param force (Input) if we've loaded a saved spectrum from disk, and the 
    #                      "processed" array literally has fewer values than the 
    #                      x-axes, and the Measurement metadata clearly shows
    #                      an ROI, then we can assume that the Measurement was
    #                      vignetted when it was saved / generated, and we really
    #                      have no choice to un-vignette it now (other than by
    #                      prefixing/suffixing zeros or something).  
    # @returns cropped spectrum
    def crop(self, spectrum, spec=None, roi=None, force=False):
        if spectrum is None:
            return

        if roi is None:
            if spec is None:
                spec = self.multispec.current_spectrometer()
            if spec is not None:
                roi = spec.settings.eeprom.get_horizontal_roi()

        if roi is None:
            return spectrum

        orig_len = len(spectrum)

        if not roi.valid() or roi.start >= orig_len or roi.end >= orig_len:
            return spectrum

        log.debug("crop: cropping spectrum of %d pixels to %d (%d to %d)", orig_len, roi.len, roi.start, roi.end)
        return roi.crop(spectrum)
        
    ##
    # Called by Controller.
    # 
    # @param pr (In/Out) ProcessedReading
    # @param settings (Input) SpectrometerSettings
    def process(self, pr, settings=None):
        if pr is None or pr.processed is None:
            return

        if settings is None:
            spec = self.multispec.current_spectrometer()
            if spec is not None:
                settings = spec.settings
        if settings is None:
            return

        roi = settings.eeprom.get_horizontal_roi()
        if roi is None:
            return 
            
        pr.processed_vignetted = self.crop(pr.processed, roi=roi)
        log.debug("process: processed_vignetted has %d pixels", len(pr.processed_vignetted))
