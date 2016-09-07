from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib import pyplot as plt

from .signal_model import *
from .widgets import *

font = {'size': 7}
matplotlib.rc('font', **font)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))


class AppWindow(QMainWindow):
    """
    This is the View-Controller part of MVC app
    """
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("EMG signal workbench")

        # Menu bars
        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Open', self.file_open, Qt.CTRL + Qt.Key_O)
        self.file_menu.addAction('&Quit', self.file_quit, Qt.CTRL + Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.main_widget = QWidget(self)
        main_layout = QHBoxLayout(self.main_widget)

        # Toolbox
        self.tools_scroll_area = QScrollArea(self)
        self.tools_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tools_widget = QWidget(self.tools_scroll_area)
        self.tools_layout = QVBoxLayout(self.tools_widget)
        self.tools_layout.setAlignment(Qt.AlignTop)

        # Group of elements related to constant shift of the signal
        self.shift_widget = ConstantShiftWidget(remove_shift_callback=self.detrend)

        # Group of elements related to rectification of the signal
        self.rect_widget = RectificationWidget(rectify_callback=self.rectify)

        # Group of elements related to filtering the signal
        self.filter_widget = FilterWidget(apply_filter_callback=self.filter_apply,
                                          reset_filter_callback=self.signal_reset)

        # Peaks detection
        self.peaks_detection_widget = PeaksDetectionWidget(detect_callback=self.peaks_detect,
                                                           reset_callback=self.peaks_detect)

        # Onset detection
        self.onset_detection_widget = OnsetDetectionWidget(detect_callback=self.onset_detect,
                                                           reset_callback=self.onset_reset)

        # Adding tools to the toolbox
        self.tools_layout.addWidget(self.shift_widget)
        self.tools_layout.addWidget(self.rect_widget)
        self.tools_layout.addWidget(self.filter_widget)
        self.tools_layout.addWidget(self.peaks_detection_widget)
        self.tools_layout.addWidget(self.onset_detection_widget)
        self.tools_widget.setLayout(self.tools_layout)
        self.tools_scroll_area.setWidgetResizable(True)
        self.tools_scroll_area.setWidget(self.tools_widget)

        self.signal_widget = SignalWidget()
        main_layout.addWidget(self.signal_widget)
        main_layout.addWidget(self.tools_scroll_area)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

    def refresh(self):
        # Get characteristics of the signal
        self.shift_widget.set_signal_mean(self.signal_widget.signal.signal_mean())

        self.signal_widget.refresh()

    def scroll_signal(self, position):
        points = self.signal_widget.signal.signal().shape[0]
        start_point = float(position) / self.signal_scrollbar.maximum() * points
        end_point = start_point + points / (self.signal_scrollbar.maximum() / self.signal_scrollbar.pageStep() + 1)
        self.signal_frame = (start_point, end_point)
        self.refresh()

    def detrend(self):
        self.signal_widget.signal.detrend()
        self.refresh()

    def rectify(self):
        self.signal_widget.signal.rectify()
        self.refresh()

    def filter_apply(self):
        cutoff = float(self.filter_widget.filter_freq_widget.edit.text()) / 1000
        btype = "lowpass" if self.filter_widget.filter_low_button.isChecked() else "highpass"
        order = int(self.filter_widget.filter_order_widget.edit.text())
        impulse_response = "iir" if self.filter_widget.filter_iir_button.isChecked() else "fir"

        self.signal_widget.signal.filter(impulse_response=impulse_response, btype=btype, cutoff=cutoff, order=order)
        self.refresh()

    def signal_reset(self):
        self.signal_widget.signal.reset()
        self.refresh()

    def peaks_detect(self):
        threshold = float(self.peaks_detection_widget.peaks_threshold_widget.edit.text())
        min_dist = int(self.peaks_detection_widget.peaks_min_dist_widget.edit.text())
        self.signal_widget.signal.find_peaks(threshold=threshold, min_dist=min_dist)
        self.refresh()

    def peaks_reset(self):
        self.signal_widget.signal.reset_peaks()
        self.refresh()

    def onset_detect(self):
        threshold = float(self.onset_detection_widget.onset_threshold_widget.edit.text())
        n_above = int(self.onset_detection_widget.onset_above_nb_widget.edit.text())
        n_below = int(self.onset_detection_widget.onset_below_nb_widget.edit.text())
        self.signal_widget.signal.find_onset(threshold=threshold, n_above=n_above, n_below=n_below)
        self.refresh()

    def onset_reset(self):
        self.signal_widget.signal.reset_onset()
        self.refresh()

    # Menu bar buttons slots
    def file_open(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter("*.edf")
        if dlg.exec_():
            signal_filename = dlg.selectedFiles()[0]
        else:
            return
        self.signal_widget.signal = SignalModel(signal_filename)
        self.signal_widget.signal_frame = (0, self.signal_widget.signal.signal().shape[0] - 1)
        self.refresh()

    def file_quit(self):
        self.close()

    def help_menu(self):
        pass
