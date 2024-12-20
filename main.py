import sys
import window
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QSize, Qt

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mt = window.MainTable()
    mt.show()
    sys.exit(app.exec())
