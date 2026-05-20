"""
DB: Simplified 25 March 2026, removed 'extension extrapolation' using just the
DB: np.interp default of repeating the last values
DB: Also changed the 'normalization' approach to align with the models
"""

import os
import numpy as np
import math
from typing import List, Optional, Tuple, Union
from scipy.interpolate import interp1d

import logging

log = logging.getLogger(__name__)

def deconvolute_spectrum(wavenumbers_out, cleaned_spectrum, fwhm):
    pad_width = 3 # multiples of FWHM
    maxIter = 25

    cleaned_spectrum = np.array(cleaned_spectrum)
    log.debug(f"Deconvolute: max spectrum input: {max(cleaned_spectrum)}")

    wavenumberPerPixel = np.diff(wavenumbers_out)
    wavenumberPerPixel = np.insert(wavenumberPerPixel, 0, wavenumberPerPixel[0])
    avgWavenumberPerPixel = np.mean(wavenumberPerPixel)
    avgPixelFWHM = fwhm / avgWavenumberPerPixel

    # pad front and end with first/last pixel
    padPixels = math.ceil(pad_width * avgPixelFWHM)
    wavenumberPerPixelPadded = np.append(np.repeat(wavenumberPerPixel[0], padPixels),
                                         np.append(wavenumberPerPixel, np.repeat(wavenumberPerPixel[-1], padPixels)))
    pixelFWHM = fwhm / wavenumberPerPixelPadded
    pixelSigma = pixelFWHM / (2 * math.sqrt(2 * math.log(2)))
    pixelSigma2 = pixelSigma * pixelSigma

    numPixelPadded = len(wavenumberPerPixelPadded)
    resolutionH = np.zeros((numPixelPadded, numPixelPadded))

    spectrumPadded = np.append(np.repeat(cleaned_spectrum[0], padPixels),
                               np.append(cleaned_spectrum, np.repeat(cleaned_spectrum[-1], padPixels)))

    pixels = np.arange(numPixelPadded)
    for row in pixels:
        # this produces a H matrix for which the 50th line here (base 0)
        # corresponds to the 51th line in R (base 1)
        # is this the reason the spectra are shifted?
        # resolutionSpectrum = np.exp(-0.5 * np.square(pixels - row) / pixelSigma2[row])
        # the following makes the H matrix the same as in R - except an extra row 0
        if pixelSigma2[row] != 0:
            resolutionSpectrum = np.exp(-0.5 * np.square(pixels - row) / pixelSigma2[row])
        else:
            # log.error(f"divide by zero: pixelSigma2[{row}] = {pixelSigma2[row]}")
            resolutionSpectrum = 1
        resolutionH[row,] = resolutionSpectrum / np.sum(resolutionSpectrum)

    origSpectrumPadded = np.array([max(0, x) for x in spectrumPadded])
    eps = 1e-5
    spectrumDeconvPadded = np.array([max(eps, x) for x in origSpectrumPadded])

    for iter in range(maxIter):
        hTimesX = np.matmul(resolutionH, spectrumDeconvPadded)
        # orig spectrum padded, extra zero point, otherwise like R
        yOverHtimesX = origSpectrumPadded / hTimesX
        # yOverHtimesX is shifted - need to adjust
        yOverHtimesX = np.append(yOverHtimesX[0], yOverHtimesX[:-1])
        fullSum = np.dot(np.transpose(resolutionH), yOverHtimesX)
        spectrumDeconvPadded = spectrumDeconvPadded * fullSum
        spectrumDeconvPadded = np.array([max(eps, x) for x in spectrumDeconvPadded])

    keepPixels = range(padPixels, len(wavenumbers_out) + padPixels)
    spectrumDeconv = spectrumDeconvPadded[keepPixels]
    log.debug(f"ANALYSIS_SIG Deconvolute: max spectrum output: {max(spectrumDeconv)}")

    return (spectrumDeconv)

def clean_spectrum(
    model: "tf.lite.Interpreter",
    wavenumbers: np.ndarray,
    spectrum: np.ndarray,
    eeprom: dict,
    deconvolute: bool,
    model_config=None
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Clean spectrum using DALAI2 model

    Args:
        model (tf.lite.Interpreter): TensorFlow Lite model
        wavenumbers (np.ndarray): Array of wavenumber values
        spectrum (np.ndarray): Array of spectrum values
        eeprom (dict): EEPROM settings
        deconvolute (bool): Whether to deconvolute the spectrum

    Returns:
        Tuple[np.ndarray, np.ndarray]: Processed wavenumbers and spectrum

    Note:
        This method is specifically for DALAI 2.0 models trained post 2025-Feb,
        which expect different inputs than previous models.

        The input spectrum is interpolated to match the model's expected
        wavenumber range before processing.

        If deconvolution is enabled, the spectrum is sharpened using the
        spectrometer's average resolution from EEPROM.

    MZ: moved from DalaiRamanID.py to prep_spectra_XS.py because it seems(?)
        SIG-only. Renamed from clean_spectrum_dalai2, since it appears to be
        the new standard (renamed old clean_spectrum to 
        clean_spectrum_dalai_normalized).
        
    DB 25 Macrh 2026: I combined both 'normalized' 'dalai2' routines into one. 
        THe idea is to use the same 'extend with np.interp' default and not use the fancy extrapolation
        any more, which seems to cause problems at times. The np.interp default of just usint the last 
        values is much more robust. We will need to clip the retruned spectrum to the actual range
        provided as input, so we are not returning values from the extrapolated region.
        
    """

    # these are the actual start and end wavenumbers AFTER ROI
    w0 = wavenumbers[0]
    we = wavenumbers[-1]

    log.debug(f"clean_spectrum: wavenumbers len {len(wavenumbers)}")
    log.debug(f"clean_spectrum: w0 {w0}, we {we}")
    
    # These are the NRD/XS parameters with the original (all-5-wide CNN) XS/NRD models to yield
    # a 400 to about 2400 wavenumber output with an implicit 1 wavenumber spacing
    # The input needs to be wider by 184 pixels on either end, these pixels are lost in the U-Net
   
    INPUT_WAVENUMBER_START = 216
    INPUT_WAVENUMBERS = 2376

    OUTPUT_WAVENUMBER_START = 400
    OUTPUT_WAVENUMBERS = 2008
    
    # We can check if we are cutting off the spectrum in the front but do not use
    # the full range of the spectrum to the end
    # that is, we could keep more from the front without losing anything in the end
    
    if w0 < OUTPUT_WAVENUMBER_START and we < OUTPUT_WAVENUMBER_START + OUTPUT_WAVENUMBERS:
        lost_at_end = OUTPUT_WAVENUMBER_START + OUTPUT_WAVENUMBERS - we
        cutoff_at_start = OUTPUT_WAVENUMBER_START - w0
        if lost_at_end > cutoff_at_start:
            # we can move all the way to the front of the available wavenumbers
            OUTPUT_WAVENUMBER_START = math.ceil(w0)
        else: 
            # we align on the end and pick a new start accordingly
            OUTPUT_WAVENUMBER_START = math.ceil(we - OUTPUT_WAVENUMBERS)
        # We adjust the input start accordingly
        INPUT_WAVENUMBER_START = OUTPUT_WAVENUMBER_START - (INPUT_WAVENUMBERS - OUTPUT_WAVENUMBERS) / 2


    input_details = model.get_input_details()
    output_details = model.get_output_details()
    input_pixels = input_details[0]["shape"][1]
    output_pixels = output_details[0]["shape"][1]

    wavenumbers_iterp = np.linspace(
        INPUT_WAVENUMBER_START,
        INPUT_WAVENUMBER_START + INPUT_WAVENUMBERS, 
        INPUT_WAVENUMBERS,
    )
    spectrum_interp = np.interp(wavenumbers_iterp, wavenumbers, spectrum)
    
    # DB: added scaling here for those models that need it
    if model_config is not None and model_config.input_must_be_normalized:
        spectrum_max = max(spectrum_interp)
        spectrum_interp = spectrum_interp / spectrum_max
    else:
        # this allows to use the same 'rescaling' code at the end for both approaches
        spectrum_max = 1.0
    
    spectrum_processed = spectrum_interp.reshape((1, -1, 1))

    model.set_tensor(input_details[0]["index"], spectrum_processed.astype(np.float32))
    model.invoke()

    output_spectrum = model.get_tensor(output_details[0]["index"])
    output_spectrum = np.array(output_spectrum)
    spectrum_AI = output_spectrum.reshape(output_pixels)

    wavenumbers_AI = np.linspace(
        OUTPUT_WAVENUMBER_START,
        OUTPUT_WAVENUMBER_START + OUTPUT_WAVENUMBERS,
        OUTPUT_WAVENUMBERS,
    )

    # rescale spectrum with max value saved at the start
    # this value was set to max = 1 for models that do not require scaling
    spectrum_AI = spectrum_AI * spectrum_max
        
    # limit output to actual spectrum wavenumber range - do not include extrapolations or such
    # the spectrum Dalai gets is the range with ROI applied

    range_indices = [i for i in range(output_pixels) if w0 <= wavenumbers_AI[i] <= we]
    start_index = range_indices[0]
    end_index = range_indices[-1]

    wavenumbers_out = wavenumbers_AI[start_index:end_index+1]
    spectrum_out = spectrum_AI[start_index:end_index+1]

    log.debug(f"clean_spectrum: wavenumbers_out[0] {wavenumbers_out[0]}, wavenumbers_out[-1] {wavenumbers_out[-1]}")
    log.debug(f"clean_spectrum: wavenumbers_out len {len(wavenumbers_out)}")

    if deconvolute:
        spectrum_out = spectrum_out - spectrum_out.min()
        log.debug("processing spectra with prep_spectra_XS.deconvolute_spectrum")
        spectrum_out = deconvolute_spectrum(wavenumbers_out, spectrum_out, eeprom.avg_resolution)

    return wavenumbers_out, spectrum_out
