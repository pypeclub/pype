from Qt import QtWidgets, QtCore, QtGui


class ColorViewer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ColorViewer, self).__init__(parent)

        self.setMinimumSize(10, 10)

        self.actual_pen = QtGui.QPen()
        self.actual_color = QtGui.QColor()

    def pen(self):
        return self.actual_pen

    def setPen(self, pen):
        self.actual_pen = pen

    def color(self):
        return self.actual_color

    def setColor(self, color):
        self.actual_color = color

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(self.actual_pen)
        painter.setBrush(QtGui.QBrush(self.actual_color))
        painter.drawRect(
            QtCore.QRect(2, 2, self.width() - 4, self.height() - 4)
        )
        painter.end()

    def changeColor(self, color):
        self.actual_color = color
        self.update()
