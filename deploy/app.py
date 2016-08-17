from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import mne

font = {'size': 7}

matplotlib.rc('font', **font)


class AppWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setWindowTitle("EMG signal workbench")

        self.file_menu = QMenu('&File', self)
        self.file_menu.addAction('&Open', self.file_open, Qt.CTRL + Qt.Key_O)
        self.file_menu.addAction('&Quit', self.file_quit, Qt.CTRL + Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.main_widget = QWidget(self)
        main_layout = QHBoxLayout(self.main_widget)

        self.signal_figure = Figure(figsize=(16, 9), dpi=150)
        self.axes = self.signal_figure.add_subplot(111)

        self.tools_widget = QWidget(self)
        self.tools_layout = QVBoxLayout(self.tools_widget)
        self.tools_layout.setAlignment(Qt.AlignTop)
        self.shift_groupbox = QGroupBox()
        self.shift_group_layout = QHBoxLayout()
        self.shift_label = QLabel("Mean: ")
        self.shift_button = QPushButton("Detrend")
        self.shift_button.clicked.connect(self.detrend)
        self.shift_group_layout.addWidget(self.shift_button)
        self.shift_group_layout.addWidget(self.shift_label)
        self.shift_groupbox.setLayout(self.shift_group_layout)

        self.tools_layout.addWidget(self.shift_groupbox)
        self.tools_widget.setLayout(self.tools_layout)

        self.signal_canvas = FigureCanvas(self.signal_figure)
        main_layout.addWidget(self.signal_canvas)
        main_layout.addWidget(self.tools_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.setFixedSize(800, 400)

        self.signal_dataframe = None

    def file_open(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter("*.edf")
        if dlg.exec():
            signal_filename = dlg.selectedFiles()[0]
            signal_data = mne.io.read_raw_edf(signal_filename, preload=True)
            self.signal_dataframe = signal_data.to_data_frame()
            self.signal_redraw()
            print("123")

    def signal_redraw(self):
        emgz_signal = self.signal_dataframe['EMGZ']
        self.axes.plot(emgz_signal)
        self.signal_canvas.setFont(QFont("normal", 12))
        self.signal_canvas.draw()

    def file_quit(self):
        self.close()

    def help_menu(self):
        pass

    def detrend(self):
        emgz_signal = self.signal_dataframe['EMGZ']
