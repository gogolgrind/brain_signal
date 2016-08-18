import mne
import numpy as np

from scipy import signal
from scipy.signal import butter, filtfilt, firwin


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
        self.dataframe['time'] = self.dataframe.index.values

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
        return np.mean(self.dataframe['EMGZ'])

    def detrend(self):
        """
        Removes constant shift of the signal
        """
        emgz_signal = self.dataframe['EMGZ']
        self.dataframe['processed'] = signal.detrend(emgz_signal.values)

    def rectify(self):
        """
        Replaces all the negative values of the signal with positive ones
        """
        emgz_signal = self.dataframe['EMGZ']
        self.dataframe['processed'] = np.abs(emgz_signal)

    def filter(self, btype="lowpass", cutoff=8, order=2):
        """
        Filters the signal by frequency
        :param btype: either "lowpass" or "highpass"
        :param cutoff: cutoff frequency (in Hz)
        :param order:
        """
        emgz_signal = self.dataframe['EMGZ']
        time = self.dataframe['time'].values
        # Take average difference in time between measurements as given in milliseconds so as to get frequency
        frequency = 1 / (np.mean(np.diff(time)) * 0.001)
        # Nyquist frequency
        nyq = 0.5 * frequency
        normal_cutoff = cutoff / nyq
        b, a = butter(order, normal_cutoff, btype=btype)
        filtered = filtfilt(b, a, emgz_signal)
        self.dataframe['processed'] = filtered
