from PyQt4.QtCore import *
from PyQt4.QtGui import *

import matplotlib
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from .signal_model import *

font = {'size': 7}
matplotlib.rc('font', **font)


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

        # Place for graph of the signal
        self.signal_figure = Figure(figsize=(16, 9), dpi=150)
        self.axes = self.signal_figure.add_subplot(111)

        # Toolbox
        self.tools_widget = QWidget(self)
        self.tools_layout = QVBoxLayout(self.tools_widget)
        self.tools_layout.setAlignment(Qt.AlignTop)

        # Group of elements related to constant shift of the signal
        self.shift_groupbox = QGroupBox("Remove constant shift")
        self.shift_group_layout = QVBoxLayout()
        self.shift_group_layout.setAlignment(Qt.AlignLeft)
        self.signal_mean = 0.
        self.shift_label = QLabel("Mean: %.4f" % self.signal_mean)
        self.shift_label.setVisible(False)
        self.shift_button = QPushButton("Process")
        self.shift_button.setFixedSize(100, 25)
        self.shift_button.clicked.connect(self.detrend)
        self.shift_group_layout.addWidget(self.shift_label)
        self.shift_group_layout.addWidget(self.shift_button)
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
        self.filter_freq_widget = QWidget()
        self.filter_freq_layout = QHBoxLayout()
        self.filter_freq_label = QLabel("Frequency: ")
        self.filter_freq_edit = QLineEdit()
        self.filter_freq_edit.textChanged.connect(self.frequency_changed)
        self.filter_freq_layout.addWidget(self.filter_freq_label)
        self.filter_freq_layout.addWidget(self.filter_freq_edit)
        self.filter_freq_widget.setLayout(self.filter_freq_layout)
        self.filter_group_layout.addWidget(self.filter_freq_widget)

        # Filter order editor
        self.filter_order_widget = QWidget()
        self.filter_order_layout = QHBoxLayout()
        self.filter_order_label = QLabel("Order: ")
        self.filter_order_edit = QLineEdit()
        self.filter_order_edit.textChanged.connect(self.order_changed)
        self.filter_order_layout.addWidget(self.filter_order_label)
        self.filter_order_layout.addWidget(self.filter_order_edit)
        self.filter_order_widget.setLayout(self.filter_order_layout)
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
        self.apply_filter_button = QPushButton("Apply")
        self.apply_filter_button.clicked.connect(self.filter_apply)
        self.filter_group_layout.addWidget(self.apply_filter_button)

        self.filter_groupbox.setLayout(self.filter_group_layout)

        # Adding tools to the toolbox
        self.tools_layout.addWidget(self.shift_groupbox)
        self.tools_layout.addWidget(self.rect_groupbox)
        self.tools_layout.addWidget(self.filter_groupbox)
        self.tools_widget.setLayout(self.tools_layout)

        self.signal_canvas = FigureCanvas(self.signal_figure)
        main_layout.addWidget(self.signal_canvas)
        main_layout.addWidget(self.tools_widget)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.setFixedSize(800, 500)

        self.signal = None

    def refresh(self):
        """
        Takes all info needed from the Model and refreshes the window according to it.
        """
        # Get characteristics of the signal
        self.shift_label.setText("Mean: %.4f" % self.signal.signal_mean)

        # Refresh the graph
        emgz_signal = self.signal.signal()
        self.axes.cla()
        self.axes.plot(emgz_signal, 'b-')
        self.signal_canvas.setFont(QFont("normal", 12))
        self.signal_canvas.draw()

    # Toolbox button slots
    def detrend(self):
        self.signal.detrend()
        self.refresh()

    def rectify(self):
        self.signal.rectify()
        self.refresh()

    def filter_apply(self):
        cutoff = int(self.filter_freq_edit.text())
        btype = "lowpass" if self.filter_low_button.isChecked() else "highpass"
        order = int(self.filter_order_edit.text())

        if self.filter_iir_button.isChecked():
            self.signal.filter(btype=btype, cutoff=cutoff, order=order)
            self.refresh()

    # Toolbox line edits slots
    def frequency_changed(self, text):
        if len(text) > 0 and not text[-1].isdigit():
            self.filter_freq_edit.setText(self.filter_freq_edit.text()[:-1])

    def order_changed(self, text):
        if len(text) > 0 and not text[-1].isdigit():
            self.filter_order_edit.setText(self.filter_order_edit.text()[:-1])

    # Menu bar buttons slots
    def file_open(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.setFilter("*.edf")
        if dlg.exec():
            signal_filename = dlg.selectedFiles()[0]
            self.signal = SignalModel(signal_filename)

            # After opening of a new signal data we should redraw it and refresh statistics
            self.refresh()
            self.shift_label.setVisible(True)

    def file_quit(self):
        self.close()

    def help_menu(self):
        pass
