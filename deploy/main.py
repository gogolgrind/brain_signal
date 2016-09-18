import os
import sys
from PyQt4.QtGui import *

# os.environ["PYTHONPATH"] = "F:\\YandexDisk\\brain_company"
# os.environ["PYTHONBUFFERED"] = "1"	

from emg.app import *


def window():
    app = QApplication(sys.argv)
    window = AppWindow()
    window.show()
    # app.setActiveWindow(window)
    sys.exit(app.exec_())
    # del window, app
    # sys.exit(0)
	
if __name__ == '__main__':
    window()
    print(123)
