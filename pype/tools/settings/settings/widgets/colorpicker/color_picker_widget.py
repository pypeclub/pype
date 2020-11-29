import sys
from Qt import QtWidgets, QtCore, QtGui

from color_triangle import QtColorTriangle
from color_view import ColorViewer
from screen import screen


class ColorPickerWidget(QtWidgets.QWidget):
    colorChanged = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, parent=None):
        super(ColorPickerWidget, self).__init__(parent)

        self.colorTriangle = QtColorTriangle(self)
        self.colorView = ColorViewer(self)
        self.pickColor = QtWidgets.QPushButton("Pick a color", self)

        self.ecran = None

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.colorTriangle, 0, 0, 3, 2)
        layout.addWidget(self.colorView, 0, 2, 2, 1)
        layout.addWidget(self.pickColor, 2, 2, 1, 1)

        self.colorView.setColor(self.colorTriangle.curColor)
        self.colorTriangle.colorChanged.connect(self.colorView.changeColor)
        self.pickColor.released.connect(self.pickMode)

    def setColor(self, col):
        self.colorView.setColor(col)
        self.colorTriangle.setColor(col)

    def pickMode(self):
        self.ecran = screen()
        self.ecran.colorSelected.connect(self.colorTriangle.setColor)

    def colorChgd(self):
        self.colorChanged.emit(self.colorView.color())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = ColorPickerWidget()
    w.show()
    app.exec()
