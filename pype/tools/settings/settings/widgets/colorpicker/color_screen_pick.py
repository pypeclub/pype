import Qt
from Qt import QtWidgets, QtCore, QtGui


class PickWidget(QtWidgets.QLabel):
    colorSelected = QtCore.Signal(QtGui.QColor)

    def screen(self):
        if Qt.__binding__ in ("PyQt4", "PySide"):
            pix = QtGui.QPixmap.grabWindow(
                QtWidgets.QApplication.desktop().winId()
            )
        else:
            screen = QtWidgets.QApplication.screenAt(QtGui.QCursor.pos())
            pix = screen.grabWindow(
                QtWidgets.QApplication.desktop().winId()
            )
        self.setPixmap(pix)

        self.showFullScreen()

    def mousePressEvent(self, event):
        color = QtGui.QColor(self.pixmap().toImage().pixel(event.pos()))
        self.colorSelected.emit(color)
        self.close()
