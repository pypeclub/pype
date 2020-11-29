from Qt import QtWidgets, QtGui, QtCore


class screen(QtWidgets.QWidget):
    colorSelected = QtCore.pyqtSignal(QtGui.QColor)

    def __ini__(self, *args, **kwargs):
        super(screen, self).__init__(self, *args, **kwargs)
        self.label = QtWidgets.Qlabel(self)
        self.label.setPixmap(QtGui.QPixmap.grabWindow(
            QtWidgets.QApplication.desktop().winId()
        ))
        self.label.move(0, 0)

        self.showFullScreen()

    def mousePressEvent(self, event):
        self.colorSelected.emit(
            self.label.pixmap().toImage().pixel(event.pos())
        )
        self.close()
