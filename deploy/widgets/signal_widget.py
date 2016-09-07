from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class SignalWidget(QWidget):
    def __init__(self):
        super().__init__()
        # Place for graph of the signal
        self.signal_figure = Figure(figsize=(16, 9), dpi=150)
        self.axes = self.signal_figure.add_subplot(111)
        self.axes.autoscale(True)
        self.frame = 0

        self.main_layout = QVBoxLayout()
        self.signal_canvas = FigureCanvas(self.signal_figure)
        self.signal_canvas.setFixedSize(600, 480)
        self.toolbox_widget = NavigationToolbar(self.signal_canvas, self)
        self.main_layout.addWidget(self.signal_canvas)
        self.main_layout.addWidget(self.toolbox_widget)
        self.setLayout(self.main_layout)

        self.signal = None
        self.signal_frame = (0, 0)

    def refresh(self):
        """
        Takes all info needed from the Model and refreshes the window according to it.
        """
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
