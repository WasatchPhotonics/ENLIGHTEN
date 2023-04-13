import logging
from statistics import median

import numpy as np

from wasatch.ProcessedReading import ProcessedReading

log = logging.getLogger(__name__)

class DespikingFeature:
    """
    Provides access to the removal of cosmic spikes that could impact
    analysis. Currently only implements the algorithm in the paper by
    Whitaker and Hayes. Future improvements will provide different 
    algorithms to choose from.
    """

    def __init__(self,
                 spin_tau,
                 spin_window):
        self.spin_tau = spin_tau
        self.spin_window = spin_window

    def process(self, processed_reading: ProcessedReading) -> ProcessedReading:
        # currently the only algorithm but will likely expand to accommodate more
        return self.DarrenEtAlAlgo(processed_reading)

    def DarrenEtAlAlgo(self, processed_reading: ProcessedReading) -> ProcessedReading:
        """
        @see Whitaker, Darren, and Kevin Hayes. 
        "A Simple Algorithm for Despiking Raman Spectra." ChemRxiv (2018)
        """
        spiky_spectra = processed_reading.processed
        log.debug(f"got spiky_spectra {spiky_spectra}")
        tau_outlier_criteria = self.spin_tau.value()
        window_size_m = self.spin_window.value()
        nabla_counts = np.asarray([yt - yt_last for yt, yt_last in zip(spiky_spectra[1:],spiky_spectra[:-1])]) # 0 idx vs paper 1 idx
        med = median(nabla_counts)
        mad = median(np.abs(nabla_counts - med))
        mod_z_scores = (0.6745*(nabla_counts-med))/mad
        # nabla_counts is 1 spectra length short since its a diffing
        # paper says ends are auto set to spiky 
        # so just insert a 0 at the beginning that will be overwritten anyway
        np.insert(mod_z_scores, 0, 0) 
        mod_z_scores[0] = tau_outlier_criteria + 1
        mod_z_scores[-1] = tau_outlier_criteria + 1
        candidate_idxs = [idx[0] for idx, value in np.ndenumerate(mod_z_scores) if abs(value) > tau_outlier_criteria]
        self.interpolate_zs(spiky_spectra, mod_z_scores, candidate_idxs, tau_outlier_criteria, window_size_m)

        log.debug(f"despiked spectra is {spiky_spectra}")
        processed_reading.processed = spiky_spectra
        return processed_reading

    def interpolate_zs(self, 
                       spectra: np.ndarray, 
                       scores: np.ndarray, 
                       candidate_idxs: list[int], 
                       tau: float,
                       m: int) -> None:
        """
        @param tau, sensitivity to spikes, lower means more likely to consider 
            something a spike, Whitaker and Hayes used 6.5 for default
        @param m window size, larger window means grabs more neighbors for averaging
            in the moving window
        takes the pre-identified indicies that are believed to be spikes
        and applies the algorithm from the paper on them.
        Modification is done in place
        """
        indicator_func = lambda score, tau: 1 if abs(score) < tau else 0
        log.debug(f"candidate idx are {candidate_idxs}")
        for index in candidate_idxs:
            log.debug(f"calculation for index {index}")
            left_idx_bound = index - m
            right_idx_bound = index + m
            zs_window = [0 for x in range(2*m)] # preallocate, easiest to way imo
            spectra_window = [0 for x in range(2*m)]
            window_idx = 0
            # generate summation windows
            for i in range(left_idx_bound,right_idx_bound,1):
                # handle edges
                if i < 0:
                    zs_window[window_idx] = scores[0]
                    spectra_window[window_idx] = spectra[0]
                elif i >= len(scores):
                    zs_window[window_idx] = scores[-1]
                    spectra_window[window_idx] = spectra[-1]
                # set window values to index in main array
                else:
                    zs_window[window_idx] = scores[i]
                    spectra_window[window_idx] = spectra[i]
                window_idx += 1
            # algorithm calculations
            log.debug(f"zs window {zs_window}, spectra_window {spectra_window}")
            w_calc = list(map(
                lambda x : indicator_func(x,tau), zs_window
                ))
            w = sum(w_calc)
            log.debug(f"w values were calculated as {w_calc} sum is {w}")
            main_calc = list(map(
                lambda x: x[1]*indicator_func(x[0],tau), zip(zs_window, spectra_window) 
                ))
            main_sum = sum(main_calc)
            log.debug(f"main values were calculated as {main_calc} sum is {main_sum}")
            if w == 0:
                continue
                log.debug(f"W VALUE WAS 0")
            averaged_value = (1/w)*main_sum
            log.debug(f"assigning value {averaged_value} to spiky point with original value {spectra[index]}")
            spectra[index] = averaged_value

