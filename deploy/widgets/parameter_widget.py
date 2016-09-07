from PyQt4.QtGui import *

from functools import partial


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