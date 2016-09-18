from PyQt4.QtCore import *
from PyQt4.QtGui import *


class RectificationWidget(QGroupBox):
    def __init__(self, *__args, **__kwargs):
        super().__init__("Rectification", *__args)

        self.main_layout = QHBoxLayout()
        self.main_layout.setAlignment(Qt.AlignLeft)
        self.rect_button = QPushButton("Rectify")
        if "rectify_callback" in __kwargs:
            self.rect_button.clicked.connect(__kwargs["rectify_callback"])

        self.rect_button.setFixedSize(100, 25)
        self.main_layout.addWidget(self.rect_button)
        self.setLayout(self.main_layout)
