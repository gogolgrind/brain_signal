import mne
import numpy as np

from scipy import signal
from scipy.signal import butter, filtfilt, firwin
import peakutils


class SignalModel:
    """
    This is the Model part of MVC app
    """

    def __init__(self, filename):
        """
        Opens a file with filename given and stores data from it as pandas.Dataframe
        :param filename:
        """
        signal_data = mne.io.read_raw_edf(filename, preload=True)
        self.dataframe = signal_data.to_data_frame()
        self.reset()
        self.dataframe['time'] = self.dataframe.index.values / 1000
        self.peak_indices = None
        self.onset_indices = None

    def time(self):
        """
        :return: Timestamps of an experiment given in seconds
        """
        return self.dataframe['time']

    def signal(self, channel="EMGZ"):
        """
        :return: The signal after applying all the processing steps
        """
        return self.dataframe["p" + channel]

    def reset(self, channel="EMGZ"):
        """
        Restores the initial state of the signal
        """
        self.dataframe["p" + channel] = self.dataframe[channel]

    def signal_mean(self, channel="EMGZ"):
        return np.mean(self.dataframe["p" + channel].values)

    def detrend(self, channel="EMGZ"):
        """
        Removes constant shift of the signal
        """
        signal_data = self.dataframe["p" + channel]
        self.dataframe["p" + channel] = signal.detrend(signal_data.values)

    def rectify(self, channel="EMGZ"):
        """
        Replaces all the negative values of the signal with positive ones
        """
        signal_data = self.dataframe["p" + channel]
        self.dataframe["p" + channel] = np.abs(signal_data)

    def filter(self, impulse_response="iir", btype="lowpass", cutoff=8, order=2, channel="EMGZ"):
        """
        Filters the signal by frequency
        :param impulse_response: either "iir" or "fir" (infinite and finite impulse response)
        :param btype: either "lowpass" or "highpass"
        :param cutoff: cutoff frequency (in Hz)
        :param order:
        """
        signal_data = self.dataframe["p" + channel]
        time = self.dataframe['time'].values
        # Take average difference in time between measurements as given in milliseconds so as to get frequency
        frequency = 1 / (np.mean(np.diff(time)) * 1000)
        # Nyquist frequency
        nyq = 0.5 * frequency
        normal_cutoff = cutoff / nyq
        if impulse_response == "iir":
            b, a = butter(order, normal_cutoff, btype=btype)
            filtered = filtfilt(b, a, signal_data)
            self.dataframe["p" + channel] = filtered
        elif impulse_response == "fir":
            b = firwin(order + 1, cutoff=normal_cutoff, window='hamming', pass_zero=(btype == "lowpass"))
            filtered = filtfilt(b, 1.0, signal_data)
            self.dataframe["p" + channel] = filtered

    def find_peaks(self, threshold=0.001, min_dist=1, channel="EMGZ"):
        """
        Parameters
        ----------
        threshold: float. The minimum amplitude of peaks to be detected.
        min_dist: int constant. Minimum distance between each detected peak.

        Returns
        -------
        a 1-d numpy.array indices of signal peaks

        Notes
        -----

        References
        ----------
            - https://pythonhosted.org/PeakUtils/tutorial_a.html

        """
        self.peak_indices = peakutils.indexes(self.dataframe["p" + channel], thres=threshold, min_dist=min_dist)

    def reset_peaks(self):
        self.peak_indices = None

    def find_onset(self, threshold=0, n_above=1, n_below=0, channel="EMGZ"):
        """Detects onset in data based on amplitude threshold.

        Parameters
        ----------
        threshold: float. Minimum amplitude of `x` to detect.
        n_above : int. Minimum number of continuous samples greater than or equal to
            `threshold` to detect (but see the parameter `n_below`).
        n_below : int. Minimum number of continuous samples below `threshold` that
            will be ignored in the detection of `x` >= `threshold`.
        Returns
        -------
        indices : 1D array_like [index_initial, index_final]

        Notes
        -----
        You might have to tune the parameters according to the signal-to-noise
        characteristic of the data.

        References
        ----------
        .. [1] http://nbviewer.ipython.org/github/demotu/BMC/blob/master/notebooks/DetectOnset.ipynb


        """
        x = self.dataframe["p" + channel]
        x = np.atleast_1d(x).astype('float64')
        # deal with NaN's (by definition, NaN's are not greater than threshold)
        x[np.isnan(x)] = -np.inf
        # indices of data greater than or equal to threshold
        indices = np.nonzero(x >= threshold)[0]
        if indices.size:
            # initial and final indexes of continuous data
            indices = np.vstack((indices[np.diff(np.hstack((-np.inf, indices))) > n_below + 1],
                                 indices[np.diff(np.hstack((indices, np.inf))) > n_below + 1])).T
            # indexes of continuous data longer than or equal to n_above
            indices = indices[indices[:, 1] - indices[:, 0] >= n_above - 1, :]
        if not indices.size:
            indices = np.array([])  # standardize indicess shape
        self.onset_indices = indices

    def reset_onset(self):
        self.onset_indices = None
