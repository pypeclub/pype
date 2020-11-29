import sys
from Qt import QtWidgets, QtCore, QtGui

from color_triangle import QtColorTriangle
from color_view import ColorViewer
from color_screen_pick import PickWidget


class ColorPickerWidget(QtWidgets.QWidget):
    color_changed = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, parent=None):
        super(ColorPickerWidget, self).__init__(parent)

        self.color_triangle = QtColorTriangle(self)
        self.color_view = ColorViewer(self)
        self.btn_pick_color = QtWidgets.QPushButton("Pick a color", self)

        self.ecran = PickWidget()

        layout = QtWidgets.QGridLayout(self)
        layout.addWidget(self.color_triangle, 0, 0, 3, 2)
        layout.addWidget(self.color_view, 0, 2, 2, 1)
        layout.addWidget(self.btn_pick_color, 2, 2, 1, 1)

        self.color_view.setColor(self.color_triangle.cur_color)
        self.color_triangle.colorChanged.connect(self.color_view.changeColor)
        self.btn_pick_color.released.connect(self.pickMode)
        self.ecran.colorSelected.connect(self.color_triangle.setColor)

    def setColor(self, col):
        self.color_view.setColor(col)
        self.color_triangle.setColor(col)

    def pickMode(self):
        self.ecran = screen()

    def colorChgd(self):
        self.color_changed.emit(self.color_view.color())


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = ColorPickerWidget()
    w.show()
    app.exec()
