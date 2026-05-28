# Routines needed for preparing the measured spectra
# for the X series model
#
# update May 2025

import os
import math
import numpy as np
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

    # log.debug(f"deconvolute_spectrum: wavenumberPerPixel {wavenumberPerPixel}")
    # log.debug(f"deconvolute_spectrum: avgWavenumberPerPixel {avgWavenumberPerPixel}")
    # log.debug(f"deconvolute_spectrum: avgPixelFWHM {avgPixelFWHM}")

    # pad front and end with first/last pixel
    padPixels = math.ceil(pad_width * avgPixelFWHM)
    wavenumberPerPixelPadded = np.append(np.repeat(wavenumberPerPixel[0], padPixels),
                                         np.append(wavenumberPerPixel, np.repeat(wavenumberPerPixel[-1], padPixels)))
    pixelFWHM = fwhm / wavenumberPerPixelPadded
    pixelSigma = pixelFWHM / (2 * math.sqrt(2 * math.log(2)))
    pixelSigma2 = pixelSigma * pixelSigma

    # log.debug(f"deconvolute_spectrum: padPixels {padPixels}")
    # log.debug(f"deconvolute_spectrum: wavenumberPerPixelPadded {wavenumberPerPixelPadded}")
    # log.debug(f"deconvolute_spectrum: pixelFWHM {pixelFWHM}")
    # log.debug(f"deconvolute_spectrum: pixelSigma {pixelSigma}")
    # log.debug(f"deconvolute_spectrum: pixelSigma2 {pixelSigma2}")

    numPixelPadded = len(wavenumberPerPixelPadded)
    resolutionH = np.zeros((numPixelPadded, numPixelPadded))

    # log.debug(f"deconvolute_spectrum: numPixelPadded {numPixelPadded}")
    # log.debug(f"deconvolute_spectrum: resolutionH {resolutionH}")

    spectrumPadded = np.append(np.repeat(cleaned_spectrum[0], padPixels),
                               np.append(cleaned_spectrum, np.repeat(cleaned_spectrum[-1], padPixels)))

    # log.debug(f"deconvolute_spectrum: spectrumPadded {spectrumPadded}")

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
    log.debug(f"Deconvolute: max spectrum output: {max(spectrumDeconv)}")

    return (spectrumDeconv)

def clean_spectrum(
    model: "tf.lite.Interpreter",
    wavenumbers: np.ndarray,
    spectrum: np.ndarray,
    eeprom: dict,
    deconvolute: bool,
    model_config=None
) -> Tuple[np.ndarray, np.ndarray]:

    # wavenumbers = actual wavenumber spacing for spectrum directly as is from spectrometer
    # spectrum = corresponding intensities
    # model = X-series model 
    
    # interpolate as needed for model
    # this uses X presets: num_interp=2376, spacing_interp=1.6, start_wavenumber_output=300
    # the first two are fixed from model structure and model training
    # the last could be adjusted as needed

    # log.info(f"clean_spectrum: First Wavenumber entering dalai clean up: {wavenumbers[0]}")

    wavenumber_interp, spectrum_interp = get_interp_spectrum(wavenumbers, spectrum)
        
    # prep input
    spectrum_max = spectrum_interp.max()

    # scale down to 0 to 1
    scaled_spectrum = spectrum_interp / spectrum_max
    
    input_pixels = spectrum_interp.shape[0]
    input_spectrum = scaled_spectrum.reshape((1, -1, 1))

    # this is new for TF Lite
    input_details = model.get_input_details()
    output_details = model.get_output_details()
    input_pixels = input_details[0]['shape'][1]
    output_pixels = output_details[0]['shape'][1]
    overhang = int((input_pixels - output_pixels) / 2)
    
    # apply model
    # get and process output
    
    # this worked with keras
    # output_spectrum = model.predict(input_spectrum)

    # this is for TF Lite
    model.set_tensor(input_details[0]['index'], input_spectrum.astype(np.float32))
    model.invoke()
    output_spectrum = model.get_tensor(output_details[0]['index'])
    output_spectrum = np.array(output_spectrum)
    
    # output_pixels = output_spectrum.shape[1]
    
    # scale back up
    spectrum_AI = output_spectrum.reshape(output_pixels) * spectrum_max
    
    # this should start at 300 wavenumbers
    # overhang = int((input_pixels - output_pixels) / 2)
    wavenumbers_AI = wavenumber_interp[overhang:-overhang]

    # these are the actual start and end wavenumbers AFTER ROI
    w0 = wavenumbers[0]
    we = wavenumbers[-1]

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
        log.debug("processing spectra with prep_spectra_X.deconvolute_spectrum")
        spectrum_out = deconvolute_spectrum(wavenumbers_out, spectrum_out, eeprom.avg_resolution)

    # return wavenumbers and cleaned spectrum
    return wavenumbers_out, spectrum_out


# prepare an experimental spectra for model input
def get_interp_spectrum(wavenumbers, spectrum, num_interp=2376, spacing_interp=1.6, start_wavenumber_output=300):
    # extends the range through mirroring on the ends
    # interpolates to the provided number of pixels and wavenumber spacing and start wavenumber
    # returns interpolated spectrum
    #
    # wavenumbers = actual pixel wavenumbers of real spectrum
    # spectrum = intensities as is
    # num_interp = number of pixels to interpolate to for input of model (this is fixed, a model property)
    # spacing_interp = wavenumber spacing = 1.6 (used as such also for training)
    # start_wavenumber = where on the wavenumber axis the output shoudl start
    # From this output start, we still need to subtract 184 (this is fix with the model structure) times the wavenumber spacing
    # 184 pixels on either side

    extend_pixels = 184
    
    # these are the actual start and end wavenumbers AFTER ROI
    w0 = wavenumbers[0]
    we = wavenumbers[-1]
    
    log.debug(f"clean_spectrum: wavenumbers len {len(wavenumbers)}")
    log.debug(f"clean_spectrum: w0 {w0}, we {we}")
    
    # We can check if we are cutting off the spectrum in the front but do not use
    # the full range of the spectrum to the end
    # that is, we could keep more from the front without losing anything in the end
    
    if w0 < start_wavenumber_output and we < start_wavenumber_output + num_interp * spacing_interp:
        lost_at_end = start_wavenumber_output + num_interp * spacing_interp - we
        cutoff_at_start = start_wavenumber_output - w0
        if lost_at_end > cutoff_at_start:
            # we can move all the way to the front of the available wavenumbers
            start_wavenumber_output = math.ceil(w0)
        else: 
            # we align on the end and pick a new start accordingly
            # here we sort of assume full integer spacing, not required
            # but we use ceil and floor to end up with nice wavenumber numbers
            start_wavenumber_output = math.ceil(we - num_interp * spacing_interp)
    
    start_wavenumber = start_wavenumber_output - extend_pixels * spacing_interp

    # # interpolation axis in pixels - target wavenumber axis
    pixels_interp = np.arange(num_interp)
    end_wavenumber = start_wavenumber + spacing_interp * num_interp 

    # define interpolated wavenumbers for full input range
    # irrespective of actual spectrum
    wavenumber_interp = np.linspace(
        start_wavenumber,
        end_wavenumber,
        num_interp,
        endpoint = False,
    )

    # interpolate from provided spectrum to full input range
    # np interp will by default continue the last value if needed 
    # past the range of the actual data
    spectrum_interp = np.interp(wavenumber_interp, wavenumbers, spectrum)
       
    return wavenumber_interp, spectrum_interp
