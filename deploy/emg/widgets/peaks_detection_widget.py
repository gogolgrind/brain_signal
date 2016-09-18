from PyQt4.QtGui import *

from functools import partial

from .parameter_widget import ParameterWidget
from ..utils.widgets import sanitize_line_edit


class PeaksDetectionWidget(QGroupBox):
    def __init__(self, *__args, **__kwargs):
        super().__init__("Peaks detection", *__args)
        self.main_layout = QVBoxLayout()
        self.peaks_threshold_widget = ParameterWidget(self, "Threshold: ", "nV",
                                                      partial(sanitize_line_edit, allow_point=True))
        self.peaks_min_dist_widget = ParameterWidget(self, "Min distance: ", "points",
                                                     partial(sanitize_line_edit, allow_point=False))

        self.peaks_buttons_widget = QWidget()
        self.peaks_buttons_layout = QHBoxLayout()
        self.peaks_detect_button = QPushButton("Detect")
        if "detect_callback" in __kwargs:
            self.peaks_detect_button.clicked.connect(__kwargs["detect_callback"])

        self.peaks_reset_button = QPushButton("Reset")
        if "reset_callback" in __kwargs:
            self.peaks_reset_button.clicked.connect(__kwargs["reset_callback"])

        self.peaks_buttons_layout.addWidget(self.peaks_detect_button)
        self.peaks_buttons_layout.addWidget(self.peaks_reset_button)
        self.peaks_buttons_widget.setLayout(self.peaks_buttons_layout)
        self.main_layout.addWidget(self.peaks_threshold_widget)
        self.main_layout.addWidget(self.peaks_min_dist_widget)
        self.main_layout.addWidget(self.peaks_buttons_widget)
        self.setLayout(self.main_layout)
