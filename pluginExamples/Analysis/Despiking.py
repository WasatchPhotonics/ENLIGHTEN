import logging
from statistics import median

import numpy as np

from EnlightenPlugin import EnlightenPluginBase,    \
                            EnlightenPluginResponse, \
                            EnlightenPluginField,     \
                            EnlightenPluginConfiguration

log = logging.getLogger(__name__)

class Despiking(EnlightenPluginBase):

    def __init__(self):
        super().__init__()

    def get_configuration(self):
        fields = []

        fields.append(EnlightenPluginField(
            name="window size",
            datatype="int",
            initial=7,
            minimum=2,
            maximum=30,
            direction="input",
            ))

        fields.append(EnlightenPluginField(
            name="tau",
            datatype="float",
            initial=7,
            minimum=0.1,
            maximum=300,
            step=0.1,
            direction="input",
            ))

        return EnlightenPluginConfiguration(name            = "Despiking Plugin", 
                                            has_other_graph = True,
                                            streaming       = True,
                                            is_blocking     = False,
                                            fields          = fields,
                                            series_names    = ['Despiked',
                                                               'Detrended Diff',
                                                               'Mod Z Scores'])
    def connect(self, enlighten_info):
        return super().connect(enlighten_info)

    def process_request(self, request):
        """
        Implements an averaging window for pixels determined to be a spike.
        Spike determination is made by determining a positive outlier z score 
        followed by a negative outlier z score.
        """
        spiky_spectra = request.processed_reading.processed
        log.debug(f"got spiky_spectra {spiky_spectra}")
        settings = request.settings
        tau_outlier_criteria = request.fields["tau"]
        window_size_m = request.fields["window size"]
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
        outlier_id = np.vectorize(lambda x: abs(x) > tau_outlier_criteria)
        above_threshold = outlier_id(mod_z_scores)
        sign_diff_outliers = np.abs(np.diff(np.sign(np.multiply(above_threshold,mod_z_scores))))
        # there should be a +1 because a diff always results in an array of length n-1 of original
        candidate_idxs = [idx[0]+1 for idx, value in np.ndenumerate(sign_diff_outliers) if value == 2]
        self.interpolate_zs(spiky_spectra, mod_z_scores, candidate_idxs, tau_outlier_criteria, window_size_m)
        unit = self.enlighten_info.get_x_axis_unit()
        # set x axis info
        if unit == "nm":
            series_x = settings.wavelengths
        elif unit == "cm":
            series_x = settings.wavenumbers
        else:
            series_x = list(range(len(spiky_spectra)))

        trend_x = list(range(len(mod_z_scores)))


        log.debug(f"despiked spectra is {spiky_spectra}")
        series = {
            "Despiked": {
                "x": series_x,
                "y": spiky_spectra,
                },
              "Mod Z Scores": {
                 'x': trend_x,
                 'y': mod_z_scores,
                  }
            }
        return EnlightenPluginResponse(request, series=series)


    def interpolate_zs(self, 
                       spectra: np.ndarray, 
                       scores: np.ndarray, 
                       candidate_idxs: list[int], 
                       tau: float,
                       m: int) -> np.ndarray:
        """
        takes the pre-identified indicies that are believed to be spikes
        and apply's the algorithm from the paper on them.
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

    def disconnect(self):
        super().disconnect()
