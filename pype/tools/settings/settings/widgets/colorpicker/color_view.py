from Qt import QtWidgets, QtCore, QtGui


class ColorViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ColorViewer, self).__init__(parent)

        self.setMinimumSize(10, 10)

        self.actualPen = QtGui.QPen()
        self.actualBrush = QtGui.QBrush()
        self.actualColor = QtGui.QColor()

    def pen(self):
        return self.actualPen

    def setPen(self, pen):
        self.actualPen = pen

    def color(self):
        return self.actualColor

    def setColor(self, color):
        self.actualColor = color

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        p.setPen(self.actualPen)
        p.setBrush(QtGui.QBrush(self.actualColor))
        p.drawRect(QtCore.QRect(2, 2, self.width() - 4, self.height() - 4))
        p.end()

    def changeColor(self, color):
        self.actualColor = color
        self.update()
