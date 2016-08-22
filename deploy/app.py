from PyQt4.QtCore import *
from PyQt4.QtGui import *

from functools import partial

import matplotlib
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.widgets import Slider

from .signal_model import *

font = {'size': 7}
matplotlib.rc('font', **font)
plt.ticklabel_format(style='sci', axis='x', scilimits=(0, 0))


class AppWindow(QMainWindow):
    """
    This is the View-Controller part of MVC app
    """

    class ParameterWidget(QWidget):
        def __init__(self, parent, label, units, text_changed=None):
            """
            A widget holding a LineEdit with label describing it and label holding units of the parameter
            :param label (str).
            :param units (str).
            :param text_changed: a function invoked when the text in line edit has been changed
            """
            super().__init__(parent)
            self.layout = QHBoxLayout()
            self.label = QLabel(label)
            self.edit = QLineEdit()
            if text_changed is not None:
                text_changed = partial(text_changed, line_edit=self.edit)
                self.edit.textChanged.connect(text_changed)
            self.units = QLabel(units)
            self.layout.addWidget(self.label)
            self.layout.addWidget(self.edit)
            self.layout.addWidget(self.units)
            self.setLayout(self.layout)

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

        # Place for graph of the signal
        self.signal_figure = Figure(figsize=(16, 9), dpi=150)
        self.axes = self.signal_figure.add_subplot(111)
        self.axes.autoscale(True)
        self.frame = 0

        # Toolbox
        self.tools_scroll_area = QScrollArea(self)
        self.tools_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tools_widget = QWidget(self.tools_scroll_area)
        self.tools_layout = QVBoxLayout(self.tools_widget)
        self.tools_layout.setAlignment(Qt.AlignTop)

        # # Group of elements related to zooming
        # self.zoom_groupbox = QGroupBox("Zoom signal")
        # self.zoom_group_layout = QHBoxLayout()
        # self.zoom_group_layout.setAlignment(Qt.AlignLeft)
        # self.zoom_in_button = QPushButton("Zoom in")
        # self.zoom_in_button.setFixedSize(100, 25)
        # self.zoom_in_button.clicked.connect(self.zoom_in)
        # self.zoom_out_button = QPushButton("Zoom out")
        # self.zoom_out_button.setFixedSize(100, 25)
        # self.zoom_out_button.clicked.connect(self.zoom_out)
        # self.zoom_group_layout.addWidget(self.zoom_in_button)
        # self.zoom_group_layout.addWidget(self.zoom_out_button)
        # self.zoom_groupbox.setLayout(self.zoom_group_layout)

        # Group of elements related to constant shift of the signal
        self.shift_groupbox = QGroupBox("Remove constant shift")
        self.shift_group_layout = QHBoxLayout()
        self.shift_group_layout.setAlignment(Qt.AlignLeft)
        self.signal_mean = 0.
        self.shift_label = QLabel("Mean: %.4f" % self.signal_mean)
        self.shift_label.setVisible(False)
        self.shift_button = QPushButton("Process")
        self.shift_button.setFixedSize(100, 25)
        self.shift_button.clicked.connect(self.detrend)
        self.shift_group_layout.addWidget(self.shift_button, 1, Qt.AlignVCenter | Qt.AlignLeft)
        self.shift_group_layout.addWidget(self.shift_label, 0, Qt.AlignBottom | Qt.AlignRight)
        self.shift_groupbox.setLayout(self.shift_group_layout)

        # Group of elements related to rectification of the signal
        self.rect_groupbox = QGroupBox("Rectify signal")
        self.rect_group_layout = QHBoxLayout()
        self.rect_group_layout.setAlignment(Qt.AlignLeft)
        self.rect_button = QPushButton("Rectify")
        self.rect_button.setFixedSize(100, 25)
        self.rect_button.clicked.connect(self.rectify)
        self.rect_group_layout.addWidget(self.rect_button)
        self.rect_groupbox.setLayout(self.rect_group_layout)

        # Group of elements related to filtering the signal
        # Filter type selector
        self.filter_groupbox = QGroupBox("Filters")
        self.filter_group_layout = QVBoxLayout()
        self.filter_group_layout.setAlignment(Qt.AlignLeft)
        self.filter_low_button = QRadioButton("Low pass")
        self.filter_high_button = QRadioButton("High pass")
        self.filter_low_button.setChecked(True)
        self.filter_type_widget = QWidget()
        self.filter_type_layout = QHBoxLayout()
        self.filter_type_layout.addWidget(self.filter_low_button)
        self.filter_type_layout.addWidget(self.filter_high_button)
        self.filter_type_widget.setLayout(self.filter_type_layout)
        self.filter_group_layout.addWidget(self.filter_type_widget)

        # Filter frequency editor
        self.filter_freq_widget = AppWindow.ParameterWidget(self,
            "Frequency: ", "Hz", partial(self.sanitize_line_edit, allow_point=True))
        self.filter_group_layout.addWidget(self.filter_freq_widget)

        # Filter order editor
        self.filter_order_widget = AppWindow.ParameterWidget(self,
            "Order: ", "operations", partial(self.sanitize_line_edit, allow_point=False))
        self.filter_group_layout.addWidget(self.filter_order_widget)

        # Filter impulse response selector
        self.filter_ir_widget = QWidget()
        self.filter_ir_layout = QHBoxLayout()
        self.filter_iir_button = QRadioButton("Infinite IR")
        self.filter_iir_button.setChecked(True)
        self.filter_fir_button = QRadioButton("Finite IR")
        self.filter_ir_layout.addWidget(self.filter_iir_button)
        self.filter_ir_layout.addWidget(self.filter_fir_button)
        self.filter_ir_widget.setLayout(self.filter_ir_layout)
        self.filter_group_layout.addWidget(self.filter_ir_widget)

        # Apply configured filter button
        self.apply_reset_widget = QWidget()
        self.apply_reset_layout = QHBoxLayout()
        self.apply_filter_button = QPushButton("Apply")
        self.apply_filter_button.clicked.connect(self.filter_apply)
        self.reset_signal_button = QPushButton("Reset")
        self.reset_signal_button.clicked.connect(self.signal_reset)
        self.apply_reset_layout.addWidget(self.apply_filter_button)
        self.apply_reset_layout.addWidget(self.reset_signal_button)
        self.apply_reset_widget.setLayout(self.apply_reset_layout)
        self.filter_group_layout.addWidget(self.apply_reset_widget)
        self.filter_groupbox.setLayout(self.filter_group_layout)

        # Peaks detection
        self.peaks_detect_groupbox = QGroupBox("Peaks detection")
        self.peaks_detect_layout = QVBoxLayout()
        self.peaks_threshold_widget = AppWindow.ParameterWidget(self,
            "Threshold: ", "nV", partial(self.sanitize_line_edit, allow_point=True))
        self.peaks_min_dist_widget = AppWindow.ParameterWidget(self,
            "Min distance: ", "points", partial(self.sanitize_line_edit, allow_point=False))

        self.peaks_buttons_widget = QWidget()
        self.peaks_buttons_layout = QHBoxLayout()
        self.peaks_detect_button = QPushButton("Detect")
        self.peaks_detect_button.clicked.connect(self.peaks_detect)
        self.peaks_reset_button = QPushButton("Reset")
        self.peaks_reset_button.clicked.connect(self.peaks_reset)
        self.peaks_buttons_layout.addWidget(self.peaks_detect_button)
        self.peaks_buttons_layout.addWidget(self.peaks_reset_button)
        self.peaks_buttons_widget.setLayout(self.peaks_buttons_layout)
        self.peaks_detect_layout.addWidget(self.peaks_threshold_widget)
        self.peaks_detect_layout.addWidget(self.peaks_min_dist_widget)
        self.peaks_detect_layout.addWidget(self.peaks_buttons_widget)
        self.peaks_detect_groupbox.setLayout(self.peaks_detect_layout)

        # Onset detection
        self.onset_detect_groupbox = QGroupBox("Onset detection")
        self.onset_detect_layout = QVBoxLayout()
        self.onset_threshold_widget = AppWindow.ParameterWidget(self, "Threshold: ", "nV")
        self.onset_above_nb_widget = AppWindow.ParameterWidget(self, "Above: ", "points")
        self.onset_below_nb_widget = AppWindow.ParameterWidget(self, "Below: ", "points")

        self.onset_buttons_widget = QWidget()
        self.onset_buttons_layout = QHBoxLayout()
        self.onset_detect_button = QPushButton("Detect")
        self.onset_detect_button.clicked.connect(self.onset_detect)
        self.onset_reset_button = QPushButton("Reset")
        self.onset_reset_button.clicked.connect(self.onset_reset)
        self.onset_buttons_layout.addWidget(self.onset_detect_button)
        self.onset_buttons_layout.addWidget(self.onset_reset_button)
        self.onset_buttons_widget.setLayout(self.onset_buttons_layout)

        self.onset_detect_layout.addWidget(self.onset_threshold_widget)
        self.onset_detect_layout.addWidget(self.onset_above_nb_widget)
        self.onset_detect_layout.addWidget(self.onset_below_nb_widget)
        self.onset_detect_layout.addWidget(self.onset_buttons_widget)
        self.onset_detect_groupbox.setLayout(self.onset_detect_layout)

        # Adding tools to the toolbox
        # self.tools_layout.addWidget(self.zoom_groupbox)
        self.tools_layout.addWidget(self.shift_groupbox)
        self.tools_layout.addWidget(self.rect_groupbox)
        self.tools_layout.addWidget(self.filter_groupbox)
        self.tools_layout.addWidget(self.peaks_detect_groupbox)
        self.tools_layout.addWidget(self.onset_detect_groupbox)
        self.tools_widget.setLayout(self.tools_layout)
        self.tools_scroll_area.setWidgetResizable(True)
        self.tools_scroll_area.setWidget(self.tools_widget)

        self.signal_layout = QVBoxLayout()
        self.signal_widget = QWidget()
        self.signal_canvas = FigureCanvas(self.signal_figure)
        self.signal_canvas.setFixedSize(600, 480)
        self.signal_toolbox = NavigationToolbar(self.signal_canvas, self)
        self.signal_layout.addWidget(self.signal_canvas)
        self.signal_layout.addWidget(self.signal_toolbox)
        self.signal_widget.setLayout(self.signal_layout)
        main_layout.addWidget(self.signal_widget)
        main_layout.addWidget(self.tools_scroll_area)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        # self.setFixedSize(950, 550)

        self.signal = None
        self.signal_frame = (0, 0)

    def refresh(self):
        """
        Takes all info needed from the Model and refreshes the window according to it.
        """
        # Get characteristics of the signal
        self.shift_label.setText("Mean: %.4f" % self.signal.signal_mean())

        # Refresh the graph
        emgz_signal = self.signal.signal().values
        timestamps = self.signal.time().values
        start = int(self.signal_frame[0])
        end = int(self.signal_frame[1])

        self.axes.cla()
        self.axes.set_ylabel('Voltage, nV')
        self.axes.set_xlabel('Time, seconds')
        self.axes.set_xlim(timestamps[int(start)], timestamps[int(end)])
        self.axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        self.axes.plot(timestamps[start:end], emgz_signal[start:end], 'b-')

        self.signal_canvas.setFont(QFont("normal", 12))

        if self.signal.peak_indices is not None:
            for i in self.signal.peak_indices:
                self.axes.plot(timestamps[i], emgz_signal[i], 'ro')

        print(self.signal.onset_indices)
        if self.signal.onset_indices is not None:
            colors = ['r', 'g', 'b']
            for n, i in enumerate(self.signal.onset_indices):
                self.axes.axvline(timestamps[i][0], color=colors[n % 3], linestyle='--')
                self.axes.axvline(timestamps[i][1], color=colors[n % 3], linestyle='--')

        if start != 0 or end != self.signal.signal().shape[0]:
            width_shown = (end - start) / self.signal.signal().shape[0]

        self.signal_canvas.draw()

    # Toolbox button slots
    def zoom_in(self):
        # start = self.signal_frame[0]
        # end = (self.signal_frame[1] + start) / 2
        # self.signal_frame = (start, end)
        # page_step = self.signal_scrollbar.pageStep()
        # self.signal_scrollbar.setMaximum(page_step * (self.signal.signal().shape[0] / (end - start) - 1))
        # self.signal_scrollbar.setVisible(True)
        # self.refresh()
        pass

    def zoom_out(self):
        # if self.signal_frame[0] == 0 and self.signal_frame[1] == self.signal.signal().shape[0]:
        #     return
        # start = self.signal_frame[0]
        # end = (self.signal_frame[1] - start / 2) * 2
        # self.signal_frame = (start, end)
        # page_step = self.signal_scrollbar.pageStep()
        # self.signal_scrollbar.setMaximum(page_step * ((self.signal.signal().shape[0] - 1) / (end - start) - 1))
        # if start == 0 and end == self.signal.signal().shape[0] - 1:
        #     self.signal_scrollbar.setVisible(False)
        # self.refresh()
        pass

    def scroll_signal(self, position):
        points = self.signal.signal().shape[0]
        start_point = float(position) / self.signal_scrollbar.maximum() * points
        end_point = start_point + points / (self.signal_scrollbar.maximum() / self.signal_scrollbar.pageStep() + 1)
        self.signal_frame = (start_point, end_point)
        self.refresh()

    def detrend(self):
        self.signal.detrend()
        self.refresh()

    def rectify(self):
        self.signal.rectify()
        self.refresh()

    def filter_apply(self):
        cutoff = float(self.filter_freq_widget.edit.text()) / 1000
        btype = "lowpass" if self.filter_low_button.isChecked() else "highpass"
        order = int(self.filter_order_widget.edit.text())
        impulse_response = "iir" if self.filter_iir_button.isChecked() else "fir"

        self.signal.filter(impulse_response=impulse_response, btype=btype, cutoff=cutoff, order=order)
        self.refresh()

    def signal_reset(self):
        self.signal.reset()
        self.refresh()

    def peaks_detect(self):
        threshold = float(self.peaks_threshold_widget.edit.text())
        min_dist = int(self.peaks_min_dist_widget.edit.text())
        self.signal.find_peaks(threshold=threshold, min_dist=min_dist)
        self.refresh()

    def peaks_reset(self):
        self.signal.reset_peaks()
        self.refresh()

    def onset_detect(self):
        threshold = float(self.onset_threshold_widget.edit.text())
        n_above = int(self.onset_above_nb_widget.edit.text())
        n_below = int(self.onset_below_nb_widget.edit.text())
        self.signal.find_onset(threshold=threshold, n_above=n_above, n_below=n_below)
        self.refresh()

    def onset_reset(self):
        self.signal.reset_onset()
        self.refresh()

    # Toolbox line edits slots
    @staticmethod
    def sanitize_line_edit(text, allow_point, line_edit):
        if len(text) > 0 and not text[-1].isdigit():
            if not allow_point or text[-1] != '.' or text.count('.') > 1:
                line_edit.setText(line_edit.text()[:-1])

    # Menu bar buttons slots
    def file_open(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter("*.edf")
        if dlg.exec():
            signal_filename = dlg.selectedFiles()[0]
        else:
            return
        self.signal = SignalModel(signal_filename)
        self.signal_frame = (0, self.signal.signal().shape[0] - 1)

        # After opening of a new signal data we should redraw it and refresh statistics
        self.refresh()
        self.shift_label.setVisible(True)

    def file_quit(self):
        self.close()

    def help_menu(self):
        pass
