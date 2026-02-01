import sys
from PyQt5.QtWidgets import QApplication
from gui import CryptoEvaluator
import os
from PyQt5.QtGui import QFont  # 导入 QFont 类

plugin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'platforms')
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = plugin_path

if __name__ == '__main__':
    app = QApplication(sys.argv)

    font = QFont("Arial", 14)
    app.setFont(font)

    window = CryptoEvaluator()
    window.show()

    sys.exit(app.exec_())
