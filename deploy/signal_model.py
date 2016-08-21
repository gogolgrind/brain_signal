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
        self.dataframe['time'] = self.dataframe.index.values / 1000000

    def time(self):
        """
        :return: Timestamps of an experiment given in seconds
        """
        return self.dataframe['time']

    def signal(self):
        """
        :return: The signal after applying all the processing steps
        """
        return self.dataframe['processed']

    def reset(self):
        """
        Restores the initial state of the signal
        """
        self.dataframe['processed'] = self.dataframe['EMGZ']

    def signal_mean(self):
        return np.mean(self.dataframe['processed'].values)

    def detrend(self):
        """
        Removes constant shift of the signal
        """
        emgz_signal = self.dataframe['processed']
        self.dataframe['processed'] = signal.detrend(emgz_signal.values)

    def rectify(self):
        """
        Replaces all the negative values of the signal with positive ones
        """
        emgz_signal = self.dataframe['processed']
        self.dataframe['processed'] = np.abs(emgz_signal)

    def filter(self, impulse_response="iir", btype="lowpass", cutoff=8, order=2):
        """
        Filters the signal by frequency
        :param impulse_response: either "iir" or "fir" (infinite and finite impulse response)
        :param btype: either "lowpass" or "highpass"
        :param cutoff: cutoff frequency (in Hz)
        :param order:
        """
        emgz_signal = self.dataframe['processed']
        time = self.dataframe['time'].values
        # Take average difference in time between measurements as given in milliseconds so as to get frequency
        frequency = 1 / (np.mean(np.diff(time)) * 1000)
        # Nyquist frequency
        nyq = 0.5 * frequency
        normal_cutoff = cutoff / nyq
        if impulse_response == "iir":
            b, a = butter(order, normal_cutoff, btype=btype)
            filtered = filtfilt(b, a, emgz_signal)
            self.dataframe['processed'] = filtered
        elif impulse_response == "fir":
            b = firwin(order+1, cutoff=normal_cutoff, window='hamming', pass_zero=(btype == "lowpass"))
            filtered = filtfilt(b, 1.0, emgz_signal)
            self.dataframe['processed'] = filtered

    def find_peaks(self, threshold=0.001, min_dist=1):
        """
        :param threshold:
        :param min_dist:
        :return: a 1-d np.array of indices where peaks are located
        """
        return peakutils.indexes(self.dataframe['processed'], thres=threshold, min_dist=min_dist)
