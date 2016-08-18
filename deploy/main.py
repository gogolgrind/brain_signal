import sys
from PyQt4.QtGui import *
from deploy.app import *


def window():
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()
