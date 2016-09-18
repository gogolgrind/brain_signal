from os.path import join

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar


class SignalToolboxWidget(NavigationToolbar):
    def __init__(self, canvas, parent, resources_dir, channel_name="EMGZ", **__kwargs):
        super().__init__(canvas, parent)
        for action in self.actions():
            self.removeAction(action)
        if "move_backward_callback" in __kwargs:
            self.addAction(QIcon(join(resources_dir, "back-icon.png")),
                           "Move 5 second back", __kwargs["move_backward_callback"])

        if "move_forward_callback" in __kwargs:
            self.addAction(QIcon(join(resources_dir, "forward-icon.png")),
                           "Move 5 second forward", __kwargs["move_forward_callback"])

        self.addSeparator()

        self.addWidget(QLabel("Start: "))
        self.startLineEdit = QLineEdit()
        self.addWidget(self.startLineEdit)

        self.addWidget(QLabel("End: "))
        self.endLineEdit = QLineEdit()
        self.addWidget(self.endLineEdit)

        if "reject_signal_callback" in __kwargs:
            self.rejectButton = QPushButton("Reject")
            self.rejectButton.clicked.connect(__kwargs["reject_signal_callback"])
            self.addWidget(self.rejectButton)

        self.addSeparator()
        self.channel_name = channel_name
        self.channel_label = QLabel("asd")
        self.addWidget(self.channel_label)
        self.set_channel_name(self.channel_name)

    def set_channel_name(self, channel_name):
        self.channel_name = channel_name
        self.channel_label.setText("Channel: " + self.channel_name)
