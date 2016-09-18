from PyQt4.QtGui import *
from PyQt4.QtCore import *

from functools import partial

from .parameter_widget import ParameterWidget
from ..utils.widgets import sanitize_line_edit


class FilterWidget(QGroupBox):
    def __init__(self, *__args, **__kwargs):
        super().__init__("Filters", *__args)

        # Filter type selector
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.filter_low_button = QRadioButton("Low pass")
        self.filter_high_button = QRadioButton("High pass")
        self.filter_low_button.setChecked(True)
        self.filter_type_widget = QWidget()
        self.filter_type_layout = QHBoxLayout()
        self.filter_type_layout.addWidget(self.filter_low_button)
        self.filter_type_layout.addWidget(self.filter_high_button)
        self.filter_type_widget.setLayout(self.filter_type_layout)
        self.main_layout.addWidget(self.filter_type_widget)

        # Filter frequency editor
        self.filter_freq_widget = ParameterWidget(self, "Frequency: ", "Hz",
                                                  partial(sanitize_line_edit, allow_point=True))
        self.main_layout.addWidget(self.filter_freq_widget)

        # Filter order editor
        self.filter_order_widget = ParameterWidget(self, "Order: ", "operations",
                                                   partial(sanitize_line_edit, allow_point=False))
        self.main_layout.addWidget(self.filter_order_widget)

        # Filter impulse response selector
        self.filter_ir_widget = QWidget()
        self.filter_ir_layout = QHBoxLayout()
        self.filter_iir_button = QRadioButton("Infinite IR")
        self.filter_iir_button.setChecked(True)
        self.filter_fir_button = QRadioButton("Finite IR")
        self.filter_ir_layout.addWidget(self.filter_iir_button)
        self.filter_ir_layout.addWidget(self.filter_fir_button)
        self.filter_ir_widget.setLayout(self.filter_ir_layout)
        self.main_layout.addWidget(self.filter_ir_widget)

        # Apply configured filter button
        self.apply_reset_widget = QWidget()
        self.apply_reset_layout = QHBoxLayout()
        self.apply_filter_button = QPushButton("Apply")
        if "apply_filter_callback" in __kwargs:
            self.apply_filter_button.clicked.connect(__kwargs["apply_filter_callback"])

        self.reset_filter_button = QPushButton("Reset")
        if "reset_filter_callback" in __kwargs:
            self.reset_filter_button.clicked.connect(__kwargs["reset_filter_callback"])

        self.apply_reset_layout.addWidget(self.apply_filter_button)
        self.apply_reset_layout.addWidget(self.reset_filter_button)
        self.apply_reset_widget.setLayout(self.apply_reset_layout)
        self.main_layout.addWidget(self.apply_reset_widget)
        self.setLayout(self.main_layout)
