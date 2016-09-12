from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from ..signal_model import *
from .signal_toolbox import SignalToolboxWidget

TIME_STEP = 5


class SignalWidget(QWidget):
    def __init__(self, resources_dir, channel="EMGZ"):
        super().__init__()
        # Place for graph of the signal
        self.signal_figure = Figure(figsize=(16, 9), dpi=150)
        self.axes = self.signal_figure.add_subplot(111)
        self.axes.autoscale(True)
        self.frame = 0

        self.main_layout = QVBoxLayout()
        self.signal_canvas = FigureCanvas(self.signal_figure)
        self.signal_canvas.setFixedSize(600, 480)
        self.toolbox_widget = SignalToolboxWidget(self.signal_canvas, self, resources_dir,
                                                  move_backward_callback=self.move_backward,
                                                  move_forward_callback=self.move_forward,
                                                  reject_signal_callback=self.reject_signal)
        self.main_layout.addWidget(self.signal_canvas)
        self.main_layout.addWidget(self.toolbox_widget)
        self.setLayout(self.main_layout)

        self.signal_channel = channel
        self.signal = None
        self.signal_frame = (0, TIME_STEP)

    def move_forward(self):
        print(self.signal.time()[0][0])
        if self.signal_frame[1] + TIME_STEP >= self.signal.time()[0][self.signal.signal().shape[0] - 1]:
            return
        print(self.signal_frame, self.signal.signal().shape)
        start, end = self.signal_frame
        self.signal_frame = start + TIME_STEP, end + TIME_STEP
        self.refresh()

    def move_backward(self):
        if self.signal_frame[0] == 0:
            return
        start, end = self.signal_frame
        self.signal_frame = start - TIME_STEP, end - TIME_STEP
        self.refresh()

    def reject_signal(self):
        print(123)
        start = int(self.toolbox_widget.startLineEdit.text())
        end = int(self.toolbox_widget.endLineEdit.text())
        start_pos = np.where(self.signal.time() >= start)[0][0]
        end_pos = np.where(self.signal.time() >= end)[0][0]
        self.signal.reject(start_pos, end_pos)
        self.refresh()

    def load_signal(self, filename):
        self.signal = SignalModel(filename)

    def load_events(self, filename):
        self.signal.set_events(filename)
        self.refresh()

    def refresh(self):
        """
        Takes all info needed from the Model and refreshes the window according to it.
        """
        # Refresh the graph
        signal_data = self.signal.signal().values
        timestamps = self.signal.time().values
        start = int(self.signal_frame[0])
        start_point = np.where(timestamps >= start)[0][0]
        end = int(self.signal_frame[1])
        rightmost_points = np.where(timestamps >= end)
        if rightmost_points[0].shape[0] != 0:
            end_point = min(rightmost_points[0][0], signal_data.shape[0])
        else:
            end_point = signal_data.shape[0]

        self.axes.cla()
        self.axes.set_ylabel('Voltage, nV')
        self.axes.set_xlabel('Time, seconds')
        print(signal_data[start_point:end_point].min(), signal_data[start_point:end_point].max())
        to_plot = signal_data[start_point:end_point]
        y_limits = to_plot.min() * (1.2 if to_plot.min() < 0 else 0.8), \
                   to_plot.max() * (1.2 if to_plot.max() > 0 else 0.8)
        self.axes.set_ylim(*y_limits)
        self.axes.set_xlim(start - 0.02, start + TIME_STEP + 0.02)
        self.axes.ticklabel_format(style='sci', axis='y', scilimits=(0, 0))
        self.axes.plot(timestamps[start_point:end_point], to_plot, 'b-')

        self.signal_canvas.setFont(QFont("normal", 12))

        if self.signal.peak_indices is not None:
            for i in self.signal.peak_indices:
                self.axes.plot(timestamps[i], signal_data[i], 'ro')

        print(self.signal.onset_indices)
        colors = ['r', 'g', 'b']
        if self.signal.onset_indices is not None:
            for n, i in enumerate(self.signal.onset_indices):
                self.axes.axvline(timestamps[i][0], color=colors[n % 3], linestyle='--')
                self.axes.axvline(timestamps[i][1], color=colors[n % 3], linestyle='--')

        if self.signal.events is not None:
            for time, event_type in self.signal.events:
                if start <= time <= end:
                    self.axes.axvline(time, color='r', linestyle='-')
                    print(time)
                    text_shift, alignment = (0.5, 'left') if time - start <= end - time else (- 0.5, 'right')
                    self.axes.annotate(event_type,
                                       xy=(time, y_limits[1] * 0.85),
                                       xytext=(time + text_shift, y_limits[1] * 0.75),
                                       horizontalalignment=alignment,
                                       arrowprops=dict(
                                           facecolor='black',
                                           shrink=0.05,
                                           width=2
                                       ), )

        self.signal_canvas.draw()
