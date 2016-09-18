from PyQt4.QtGui import *
from PyQt4.QtCore import *

from functools import partial

from .parameter_widget import ParameterWidget
from ..utils.widgets import sanitize_line_edit

class OnsetDetectionWidget(QGroupBox):
    def __init__(self, *__args, **__kwargs):
        super().__init__("Onset detection", *__args)
        self.main_layout = QVBoxLayout()
        self.onset_threshold_widget = ParameterWidget(self, "Threshold: ", "nV",
                                                      partial(sanitize_line_edit, allow_point=True))
        self.onset_above_nb_widget = ParameterWidget(self, "Above: ", "points",
                                                     partial(sanitize_line_edit, allow_point=False))
        self.onset_below_nb_widget = ParameterWidget(self, "Below: ", "points",
                                                     partial(sanitize_line_edit, allow_point=False))

        self.onset_buttons_widget = QWidget()
        self.onset_buttons_layout = QHBoxLayout()
        self.onset_detect_button = QPushButton("Detect")
        if "detect_callback" in __kwargs:
            self.onset_detect_button.clicked.connect(__kwargs["detect_callback"])

        self.onset_reset_button = QPushButton("Reset")
        if "reset_callback" in __kwargs:
            self.onset_reset_button.clicked.connect(__kwargs["reset_callback"])

        self.onset_buttons_layout.addWidget(self.onset_detect_button)
        self.onset_buttons_layout.addWidget(self.onset_reset_button)
        self.onset_buttons_widget.setLayout(self.onset_buttons_layout)

        self.main_layout.addWidget(self.onset_threshold_widget)
        self.main_layout.addWidget(self.onset_above_nb_widget)
        self.main_layout.addWidget(self.onset_below_nb_widget)
        self.main_layout.addWidget(self.onset_buttons_widget)
        self.setLayout(self.main_layout)