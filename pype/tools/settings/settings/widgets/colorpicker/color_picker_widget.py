import sys
from Qt import QtWidgets, QtCore, QtGui

from color_triangle import QtColorTriangle
from color_view import ColorViewer
from color_screen_pick import PickWidget

slide_style = """
QSlider::groove:horizontal {
    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #000, stop: 1 #fff);
    height: 8px;
    border-radius: 4px;
}

QSlider::handle:horizontal {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ddd, stop:1 #bbb);
    border: 1px solid #777;
    width: 8px;
    margin-top: -1px;
    margin-bottom: -1px;
    border-radius: 4px;
}

QSlider::handle:horizontal:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eee, stop:1 #ddd);
    border: 1px solid #444;ff
    border-radius: 4px;
}"""
class ColorPickerWidget(QtWidgets.QWidget):
    color_changed = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, parent=None):
        super(ColorPickerWidget, self).__init__(parent)

        # Eye picked widget
        pick_widget = PickWidget()

        # Color triangle
        color_triangle = QtColorTriangle(self)
        color_triangle.setFixedSize(150, 150)

        # Color utils
        utils_widget = QtWidgets.QWidget(self)
        utils_layout = QtWidgets.QVBoxLayout(utils_widget)
        utils_layout.setContentsMargins(0, 0, 0, 0)

        # Color preview
        color_view = ColorViewer(utils_widget)
        # Color pick button
        btn_pick_color = QtWidgets.QPushButton("Pick a color", utils_widget)
        # Opacity slider
        opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, utils_widget)
        opacity_slider.setSingleStep(1)
        opacity_slider.setMinimum(0)
        opacity_slider.setMaximum(255)
        opacity_slider.setStyleSheet(slide_style)
        opacity_slider.setValue(255)

        utils_layout.addWidget(color_view)
        utils_layout.addWidget(opacity_slider)
        utils_layout.addWidget(btn_pick_color)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(color_triangle, 1)
        layout.addWidget(utils_widget, 0)

        color_view.setColor(color_triangle.cur_color)

        color_triangle.colorChanged.connect(self.color_changed)
        btn_pick_color.released.connect(self.pick_color)
        pick_widget.colorSelected.connect(self.color_changed)
        opacity_slider.valueChanged.connect(self.opacity_changed)

        self.pick_widget = pick_widget

        self.color_triangle = color_triangle
        self.color_view = color_view
        self.opacity_slider = opacity_slider
        self.btn_pick_color = btn_pick_color

    def setColor(self, color):
        self.opacity_changed(color.alpha())
        self.color_changed(color.alpha())

    def pick_color(self):
        self.pick_widget.screen()

    def color_changed(self, color):
        self.color_view.setColor(color)
        self.color_triangle.setColor(color)

    def opacity_changed(self, alpha):
        self.color_view.setAlpha(alpha)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    w = ColorPickerWidget()
    w.show()
    app.exec()
