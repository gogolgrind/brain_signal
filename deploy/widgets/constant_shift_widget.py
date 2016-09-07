from PyQt4.QtCore import *
from PyQt4.QtGui import *


class ConstantShiftWidget(QGroupBox):
    def __init__(self, *__args, **__kwargs):
        super().__init__("Constant shift", *__args)

        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.mean_label = QLabel("Mean: %.4f" % 0)
        self.mean_label.setVisible(False)
        self.shift_button = QPushButton("Process")
        if "remove_shift_callback" in __kwargs:
            self.shift_button.clicked.connect(__kwargs["remove_shift_callback"])

        self.shift_button.setFixedSize(100, 25)
        self.main_layout.addWidget(self.shift_button, 1, Qt.AlignVCenter | Qt.AlignLeft)
        self.main_layout.addWidget(self.mean_label, 0, Qt.AlignBottom | Qt.AlignRight)
        self.setLayout(self.main_layout)

    def set_signal_mean(self, mean):
        self.mean_label.setText("Mean: %.4f" % mean)
        self.mean_label.setVisible(True)
