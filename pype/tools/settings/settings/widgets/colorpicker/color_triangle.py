import math
from Qt import QtWidgets, QtCore, QtGui

QT_VERSION = 5

TWOPI = math.pi * 2

IdleState = object()
SelectingHueState = object()
SelectingSatValueState = object()


class DoubleColor:
    def __init__(self, r, g=None, b=None):
        if g is None:
            g = r.g
            b = r.b
            r = r.r
        self.r = r
        self.g = g
        self.b = b


class Vertex:
    def __init__(self, color, point):
        if isinstance(color, QtCore.Qt.GlobalColor):
            color = QtGui.QColor(color)

        if isinstance(color, QtGui.QColor):
            color = DoubleColor(
                float(color.red()),
                float(color.green()),
                float(color.blue())
            )

        self.color = color
        self.point = point


class QtColorTriangle(QtWidgets.QWidget):
    colorChanged = QtCore.pyqtSignal(QtGui.QColor)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum
        )
        self.setFocusPolicy(QtCore.Qt.StrongFocus)

        self.a = float()
        self.b = float()
        self.c = float()

        self.bg = QtGui.QImage(self.sizeHint(), QtGui.QImage.Format_RGB32)
        self.curColor = QtGui.QColor()
        self.pa = QtCore.QPointF()
        self.pb = QtCore.QPointF()
        self.pc = QtCore.QPointF()
        self.pd = QtCore.QPointF()

        self.curHue = int()
        self.mustGenerateBackground = True

        self.penWidth = int()
        self.ellipseSize = int()
        self.outerRadius = int()
        self.selectorPos = QtCore.QPointF()

        self.selMode = IdleState

        tmp = QtGui.QColor()
        tmp.setHsv(76, 184, 206)
        self.setColor(tmp)

    def setColor(self, col):
        if col == self.curColor:
            return

        self.curColor = col

        h, s, v, _a = self.curColor.getHsv()

        # Never use an invalid hue to display colors
        if h != -1:
            self.curHue = h

        self.a = (((360 - self.curHue) * TWOPI) / 360.0)
        self.a += math.pi / 2.0
        if self.a > TWOPI:
            self.a -= TWOPI

        self.b = self.a + TWOPI / 3
        self.c = self.b + TWOPI / 3

        if self.b > TWOPI:
            self.b -= TWOPI
        if self.c > TWOPI:
            self.c -= TWOPI

        cx = float(self.contentsRect().center().x())
        cy = float(self.contentsRect().center().y())
        innerRadius = self.outerRadius - (self.outerRadius / 5.0)
        pointerRadius = self.outerRadius - (self.outerRadius / 10.0)

        self.pa = QtCore.QPointF(
            cx + (math.cos(self.a) * innerRadius),
            cy - (math.sin(self.a) * innerRadius)
        )
        self.pb = QtCore.QPointF(
            cx + (math.cos(self.b) * innerRadius),
            cy - (math.sin(self.b) * innerRadius)
        )
        self.pc = QtCore.QPointF(
            cx + (math.cos(self.c) * innerRadius),
            cy - (math.sin(self.c) * innerRadius)
        )
        self.pd = QtCore.QPointF(
            cx + (math.cos(self.a) * pointerRadius),
            cy - (math.sin(self.a) * pointerRadius)
        )

        self.selectorPos = self.pointFromColor(self.curColor)
        self.update()

        self.colorChanged.emit(self.curColor)

    def sizeHint(self):
        return QtCore.QSize(100, 100)

    def heightForWidth(self, width):
        return width

    # Internal
    def polish(self):
        outer_radius_width = (self.contentsRect().width() - 1) / 2
        outer_radius_height = (self.contentsRect().height() - 1) / 2
        if outer_radius_height < outer_radius_width:
            self.outerRadius = outer_radius_height
        else:
            self.outerRadius = outer_radius_width

        self.penWidth = int(math.floor(self.outerRadius / 50.0))
        self.ellipseSize = int(math.floor(self.outerRadius / 10))

        cx = float(self.contentsRect().center().x())
        cy = float(self.contentsRect().center().y())

        self.pa = QtCore.QPointF(
            cx + (math.cos(self.a) * (self.outerRadius - (self.outerRadius / 5.0))),
            cy - (math.sin(self.a) * (self.outerRadius - (self.outerRadius / 5.0)))
        )
        self.pb = QtCore.QPointF(
            cx + (math.cos(self.b) * (self.outerRadius - (self.outerRadius / 5.0))),
            cy - (math.sin(self.b) * (self.outerRadius - (self.outerRadius / 5.0)))
        )
        self.pc = QtCore.QPointF(
            cx + (math.cos(self.c) * (self.outerRadius - (self.outerRadius / 5.0))),
            cy - (math.sin(self.c) * (self.outerRadius - (self.outerRadius / 5.0)))
        )
        self.pd = QtCore.QPointF(
            cx + (math.cos(self.a) * (self.outerRadius - (self.outerRadius / 10.0))),
            cy - (math.sin(self.a) * (self.outerRadius - (self.outerRadius / 10.0)))
        )

        self.selectorPos = self.pointFromColor(self.curColor)

        self.update()

    def paintEvent(self, event):
        p = QtGui.QPainter(self)
        if event.rect().intersects(self.contentsRect()):
            event_region = event.region()
            if hasattr(event_region, "intersect"):
                clip_region = event_region.intersect(self.contentsRect())
            else:
                clip_region = event_region.intersected(
                    self.contentsRect()
                )
            p.setClipRegion(clip_region)

        if self.mustGenerateBackground:
            self.genBackground()
            self.mustGenerateBackground = False

        # Blit the static generated background with the hue gradient onto
        # the double buffer.
        buf = QtGui.QImage(self.bg.copy())

        # Draw the trigon
        # h, s, v, _a = self.curColor.getHsv()

        # Find the color with only the hue, and max value and saturation
        hueColor = QtGui.QColor()
        hueColor.setHsv(self.curHue, 255, 255)

        # Draw the triangle
        self.drawTrigon(buf, self.pa, self.pb, self.pc, hueColor)

        # Slow step: convert the image to a pixmap
        pix = QtGui.QPixmap.fromImage(buf)
        painter = QtGui.QPainter(pix)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw an outline of the triangle
        # --- ORIGINAL VALUES ---
        # halfAlpha = QtGui.QColor(0, 0, 0, 128)
        # painter.setPen(QtGui.QPen(halfAlpha, 0))

        halfAlpha = QtGui.QColor(40, 40, 40, 128)
        painter.setPen(QtGui.QPen(halfAlpha, 2))

        painter.drawLine(self.pa, self.pb)
        painter.drawLine(self.pb, self.pc)
        painter.drawLine(self.pc, self.pa)

        painter.setPen(QtGui.QPen(QtCore.Qt.white, self.penWidth))
        painter.drawEllipse(
            int(self.pd.x() - self.ellipseSize / 2.0),
            int(self.pd.y() - self.ellipseSize / 2.0),
            self.ellipseSize, self.ellipseSize
        )

        # Draw the selector ellipse.
        painter.setPen(QtGui.QPen(QtCore.Qt.white, self.penWidth))
        painter.setBrush(self.curColor)
        painter.drawEllipse(
            QtCore.QRectF(
                self.selectorPos.x() - self.ellipseSize / 2.0,
                self.selectorPos.y() - self.ellipseSize / 2.0,
                self.ellipseSize + 0.5,
                self.ellipseSize + 0.5
            )
        )

        painter.end()
        # Blit
        p.drawPixmap(self.contentsRect().topLeft(), pix)
        p.end()

    def mouseMoveEvent(self, event):
        if (event.buttons() & QtCore.Qt.LeftButton) == 0:
            return

        depos = QtCore.QPointF(
            event.pos().x(),
            event.pos().y()
        )
        newColor = False

        if self.selMode is SelectingHueState:
            self.a = self.angleAt(depos, self.contentsRect())
            self.b = self.a + (TWOPI / 3.0)
            self.c = self.b + (TWOPI / 3.0)
            if self.b > TWOPI:
                self.b -= TWOPI
            if self.c > TWOPI:
                self.c -= TWOPI

            am = self.a - (math.pi / 2)
            if am < 0:
                am += TWOPI

            self.curHue = 360 - int(((am) * 360.0) / TWOPI)
            h, s, v, _a = self.curColor.getHsv()

            if self.curHue != h:
                newColor = True
                self.curColor.setHsv(self.curHue, s, v)

            cx = float(self.contentsRect().center().x())
            cy = float(self.contentsRect().center().y())

            self.pa = QtCore.QPointF(
                cx + (
                    math.cos(self.a)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                ),
                cy - (
                    math.sin(self.a)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                )
            )
            self.pb = QtCore.QPointF(
                cx + (
                    math.cos(self.b)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                ),
                cy - (
                    math.sin(self.b)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                )
            )
            self.pc = QtCore.QPointF(
                cx + (
                    math.cos(self.c)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                ),
                cy - (
                    math.sin(self.c)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                )
            )
            self.pd = QtCore.QPointF(
                cx + (
                    math.cos(self.a)
                    * (self.outerRadius - (self.outerRadius / 10.0))
                ),
                cy - (
                    math.sin(self.a)
                    * (self.outerRadius - (self.outerRadius / 10.0))
                )
            )

            self.selectorPos = self.pointFromColor(self.curColor)
        else:
            aa = Vertex(QtCore.Qt.black, self.pa)
            bb = Vertex(QtCore.Qt.black, self.pb)
            cc = Vertex(QtCore.Qt.black, self.pc)

            self.selectorPos = self.movePointToTriangle(
                depos.x(), depos.y(), aa, bb, cc
            )
            col = self.colorFromPoint(self.selectorPos)
            if (col != self.curColor):
                # Ensure that hue does not change when selecting
                # saturation and value.
                h, s, v, _a = col.getHsv()
                self.curColor.setHsv(self.curHue, s, v)
                newColor = True

        if newColor:
            self.colorChanged.emit(self.curColor)

        self.update()

    def mousePressEvent(self, event):
        # Only respond to the left mouse button.
        if event.button() != QtCore.Qt.LeftButton:
            return

        depos = QtCore.QPointF(
            event.pos().x(),
            event.pos().y()
        )
        rad = self.radiusAt(depos, self.contentsRect())
        newColor = False

        # As in mouseMoveEvent, either find the a, b, c angles or the
        # radian position of the selector, then order an update.
        if (rad > (self.outerRadius - (self.outerRadius / 5))):
            self.selMode = SelectingHueState

            self.a = self.angleAt(depos, self.contentsRect())
            self.b = self.a + TWOPI / 3.0
            self.c = self.b + TWOPI / 3.0
            if self.b > TWOPI:
                self.b -= TWOPI
            if self.c > TWOPI:
                self.c -= TWOPI

            am = self.a - math.pi / 2
            if am < 0:
                am += TWOPI

            self.curHue = 360 - int((am * 360.0) / TWOPI)
            h, s, v, _a = self.curColor.getHsv()

            if h != self.curHue:
                newColor = True
                self.curColor.setHsv(self.curHue, s, v)

            cx = float(self.contentsRect().center().x())
            cy = float(self.contentsRect().center().y())

            self.pa = QtCore.QPointF(
                cx + (
                    math.cos(self.a)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                ),
                cy - (
                    math.sin(self.a)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                )
            )
            self.pb = QtCore.QPointF(
                cx + (
                    math.cos(self.b)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                ),
                cy - (
                    math.sin(self.b)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                )
            )
            self.pc = QtCore.QPointF(
                cx + (
                    math.cos(self.c)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                ),
                cy - (
                    math.sin(self.c)
                    * (self.outerRadius - (self.outerRadius / 5.0))
                )
            )
            self.pd = QtCore.QPointF(
                cx + (
                    math.cos(self.a)
                    * (self.outerRadius - (self.outerRadius / 10.0))
                ),
                cy - (
                    math.sin(self.a)
                    * (self.outerRadius - (self.outerRadius / 10.0))
                )
            )

            self.selectorPos = self.pointFromColor(self.curColor)
            self.colorChanged.emit(self.curColor)
        else:
            self.selMode = SelectingSatValueState

            aa = Vertex(QtCore.Qt.black, self.pa)
            bb = Vertex(QtCore.Qt.black, self.pb)
            cc = Vertex(QtCore.Qt.black, self.pc)

            self.selectorPos = self.movePointToTriangle(
                depos.x(), depos.y(), aa, bb, cc
            )
            col = self.colorFromPoint(self.selectorPos)
            if col != self.curColor:
                self.curColor = col
                newColor = True

        if newColor:
            self.colorChanged.emit(self.curColor)

        self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.selMode = IdleState

    def keyPressEvent(self, event):
        key = event.key()
        if key == QtCore.Qt.Key_Left:
            self.curHue -= 1
            if self.curHue < 0:
                self.curHue += 360
            h, s, v, _a = self.curColor.getHsv()

            tmp = QtGui.QColor()
            tmp.setHsv(self.curHue, s, v)
            self.setColor(tmp)

        elif key == QtCore.Qt.Key_Right:
            self.curHue += 1
            if (self.curHue > 359):
                self.curHue -= 360
            h, s, v, _a = self.curColor.getHsv()
            tmp = QtGui.QColor()
            tmp.setHsv(self.curHue, s, v)
            self.setColor(tmp)

        elif key == QtCore.Qt.Key_Up:
            h, s, v, _a = self.curColor.getHsv()
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                if (s > 5):
                    s -= 5
                else:
                    s = 0
            else:
                if (v > 5):
                    v -= 5
                else:
                    v = 0

            tmp = QtGui.QColor()
            tmp.setHsv(self.curHue, s, v)
            self.setColor(tmp)

        elif key == QtCore.Qt.Key_Down:
            h, s, v, _a = self.curColor.getHsv()
            if event.modifiers() & QtCore.Qt.ShiftModifier:
                if s < 250:
                    s += 5
                else:
                    s = 255
            else:
                if v < 250:
                    v += 5
                else:
                    v = 255

            tmp = QtGui.QColor()
            tmp.setHsv(self.curHue, s, v)
            self.setColor(tmp)

    def resizeEvent(self, event):
        outer_radius_width = (self.contentsRect().width() - 1) / 2
        outer_radius_height = (self.contentsRect().height() - 1) / 2
        if outer_radius_height < outer_radius_width:
            outerRadius = outer_radius_height
        else:
            outerRadius = outer_radius_width

        self.penWidth = int(math.floor(outerRadius / 50.0))
        self.ellipseSize = int(math.floor(outerRadius / 10))
        self.outerRadius = outerRadius

        cx = float(self.contentsRect().center().x())
        cy = float(self.contentsRect().center().y())

        self.pa = QtCore.QPointF(
            cx + (math.cos(self.a) * (outerRadius - (outerRadius / 5.0))),
            cy - (math.sin(self.a) * (outerRadius - (outerRadius / 5.0)))
        )
        self.pb = QtCore.QPointF(
            cx + (math.cos(self.b) * (outerRadius - (outerRadius / 5.0))),
            cy - (math.sin(self.b) * (outerRadius - (outerRadius / 5.0)))
        )
        self.pc = QtCore.QPointF(
            cx + (math.cos(self.c) * (outerRadius - (outerRadius / 5.0))),
            cy - (math.sin(self.c) * (outerRadius - (outerRadius / 5.0)))
        )
        self.pd = QtCore.QPointF(
            cx + (math.cos(self.a) * (outerRadius - (outerRadius / 10.0))),
            cy - (math.sin(self.a) * (outerRadius - (outerRadius / 10.0)))
        )

        # Find the current position of the selector
        self.selectorPos = self.pointFromColor(self.curColor)

        self.mustGenerateBackground = True
        self.update()

    def drawTrigon(self, buf, pa, pb, pc, color):
        # Create three Vertex objects. A Vertex contains a double-point
        # coordinate and a color.
        # pa is the tip of the arrow
        # pb is the black corner
        # pc is the white corner
        p1 = Vertex(color, pa)
        p2 = Vertex(QtCore.Qt.black, pb)
        p3 = Vertex(QtCore.Qt.white, pc)

        # Sort. Make p1 above p2, which is above p3 (using y coordinate).
        # Bubble sorting is fastest here.
        if p1.point.y() > p2.point.y():
            p1, p2 = p2, p1
        if p1.point.y() > p3.point.y():
            p1, p3 = p3, p1
        if p2.point.y() > p3.point.y():
            p2, p3 = p3, p2

        # All the three y deltas are >= 0
        p1p2ydist = float(p2.point.y() - p1.point.y())
        p1p3ydist = float(p3.point.y() - p1.point.y())
        p2p3ydist = float(p3.point.y() - p2.point.y())
        p1p2xdist = float(p2.point.x() - p1.point.x())
        p1p3xdist = float(p3.point.x() - p1.point.x())
        p2p3xdist = float(p3.point.x() - p2.point.x())

        # The first x delta decides wether we have a lefty or a righty
        # trigon.
        lefty = p1p2xdist < 0

        # Left and right colors and X values. The key in this map is the
        # y values. Our goal is to fill these structures with all the
        # information needed to do a single pass top-to-bottom,
        # left-to-right drawing of the trigon.
        leftColors = {}
        rightColors = {}
        leftX = {}
        rightX = {}
        # QVarLengthArray<DoubleColor, 2000> leftColors;
        # QVarLengthArray<DoubleColor, 2000> rightColors;
        # QVarLengthArray<double, 2000> leftX;
        # QVarLengthArray<double, 2000> rightX;

        # leftColors.resize(int(floor(p3.point.y() + 1)));
        # rightColors.resize(int(floor(p3.point.y() + 1)));
        # leftX.resize(int(floor(p3.point.y() + 1)));
        # rightX.resize(int(floor(p3.point.y() + 1)));

        # Scan longy - find all left and right colors and X-values for
        # the tallest edge (p1-p3).
        # Initialize with known values
        x = p1.point.x()
        source = p1.color
        dest = p3.color
        r = source.r
        g = source.g
        b = source.b
        y1 = int(math.floor(p1.point.y()))
        y2 = int(math.floor(p3.point.y()))

        # Find slopes (notice that if the y dists are 0, we don't care
        # about the slopes)
        xdelta = 0.0
        rdelta = 0.0
        gdelta = 0.0
        bdelta = 0.0
        if p1p3ydist != 0.0:
            xdelta = p1p3xdist / p1p3ydist
            rdelta = (dest.r - r) / p1p3ydist
            gdelta = (dest.g - g) / p1p3ydist
            bdelta = (dest.b - b) / p1p3ydist

        # Calculate gradients using linear approximation
        for y in range(y1, y2):
            if lefty:
                rightColors[y] = DoubleColor(r, g, b)
                rightX[y] = x
            else:
                leftColors[y] = DoubleColor(r, g, b)
                leftX[y] = x

            r += rdelta
            g += gdelta
            b += bdelta
            x += xdelta

        # Scan top shorty - find all left and right colors and x-values
        # for the topmost of the two not-tallest short edges.
        x = p1.point.x()
        source = p1.color
        dest = p2.color
        r = source.r
        g = source.g
        b = source.b
        y1 = int(math.floor(p1.point.y()))
        y2 = int(math.floor(p2.point.y()))

        # Find slopes (notice that if the y dists are 0, we don't care
        # about the slopes)
        xdelta = 0.0
        rdelta = 0.0
        gdelta = 0.0
        bdelta = 0.0
        if p1p2ydist != 0.0:
            xdelta = p1p2xdist / p1p2ydist
            rdelta = (dest.r - r) / p1p2ydist
            gdelta = (dest.g - g) / p1p2ydist
            bdelta = (dest.b - b) / p1p2ydist

        # Calculate gradients using linear approximation
        for y in range(y1, y2):
            if lefty:
                leftColors[y] = DoubleColor(r, g, b)
                leftX[y] = x
            else:
                rightColors[y] = DoubleColor(r, g, b)
                rightX[y] = x

            r += rdelta
            g += gdelta
            b += bdelta
            x += xdelta

        # Scan bottom shorty - find all left and right colors and
        # x-values for the bottommost of the two not-tallest short edges.
        x = p2.point.x()
        source = p2.color
        dest = p3.color
        r = source.r
        g = source.g
        b = source.b
        y1 = int(math.floor(p2.point.y()))
        y2 = int(math.floor(p3.point.y()))

        # Find slopes (notice that if the y dists are 0, we don't care
        # about the slopes)
        xdelta = 0.0
        rdelta = 0.0
        gdelta = 0.0
        bdelta = 0.0
        if p2p3ydist != 0.0:
            xdelta = p2p3xdist / p2p3ydist
            rdelta = (dest.r - r) / p2p3ydist
            gdelta = (dest.g - g) / p2p3ydist
            bdelta = (dest.b - b) / p2p3ydist

        # Calculate gradients using linear approximation
        for y in range(y1, y2):
            if lefty:
                leftColors[y] = DoubleColor(r, g, b)
                leftX[y] = x
            else:
                rightColors[y] = DoubleColor(r, g, b)
                rightX[y] = x

            r += rdelta
            g += gdelta
            b += bdelta
            x += xdelta

        # Inner loop. For each y in the left map of x-values, draw one
        # line from left to right.
        p3yfloor = int(math.floor(p3.point.y()))
        p1yfloor = int(math.floor(p1.point.y()))
        for y in range(p1yfloor, p3yfloor):
            lx = leftX[y]
            rx = rightX[y]

            lxi = int(math.floor(lx))
            rxi = int(math.floor(rx))
            rc = rightColors[y]
            lc = leftColors[y]

            # if the xdist is 0, don't draw anything.
            xdist = rx - lx
            if xdist != 0.0:
                r = lc.r
                g = lc.g
                b = lc.b
                rdelta = (rc.r - r) / xdist
                gdelta = (rc.g - g) / xdist
                bdelta = (rc.b - b) / xdist

                # Inner loop 2. Draws the line from left to right.
                for x in range(lxi, rxi + 1):
                    buf.setPixel(x, y, QtGui.qRgb(int(r), int(g), int(b)))
                    r += rdelta
                    g += gdelta
                    b += bdelta

    # Private
    def radiusAt(self, pos, rect):
        mousexdist = pos.x() - float(rect.center().x())
        mouseydist = pos.y() - float(rect.center().y())
        return math.sqrt(mousexdist * mousexdist + mouseydist * mouseydist)

    def angleAt(self, pos, rect):
        mousexdist = pos.x() - float(rect.center().x())
        mouseydist = pos.y() - float(rect.center().y())
        mouserad = math.sqrt(
            mousexdist * mousexdist + mouseydist * mouseydist
        )
        if mouserad == 0.0:
            return 0.0

        angle = math.acos(mousexdist / mouserad)
        if mouseydist >= 0:
            angle = TWOPI - angle

        return angle

    def pointFromColor(self, col):
        # Simplifications for the corner cases.
        if col == QtCore.Qt.black:
            return self.pb
        elif col == QtCore.Qt.white:
            return self.pc

        # Find the x and y slopes
        ab_deltax = self.pb.x() - self.pa.x()
        ab_deltay = self.pb.y() - self.pa.y()
        bc_deltax = self.pc.x() - self.pb.x()
        bc_deltay = self.pc.y() - self.pb.y()
        ac_deltax = self.pc.x() - self.pa.x()
        ac_deltay = self.pc.y() - self.pa.y()

        # Extract the h,s,v values of col.
        hue, sat, val, _a = col.getHsv()

        # Find the line that passes through the triangle where the value
        # is equal to our color's value.
        p1 = self.pa.x() + (ab_deltax * float(255 - val)) / 255.0
        q1 = self.pa.y() + (ab_deltay * float(255 - val)) / 255.0
        p2 = self.pb.x() + (bc_deltax * float(val)) / 255.0
        q2 = self.pb.y() + (bc_deltay * float(val)) / 255.0

        # Find the line that passes through the triangle where the
        # saturation is equal to our color's value.
        p3 = self.pa.x() + (ac_deltax * float(255 - sat)) / 255.0
        q3 = self.pa.y() + (ac_deltay * float(255 - sat)) / 255.0
        p4 = self.pb.x()
        q4 = self.pb.y()

        # Find the intersection between these lines.
        x = 0
        y = 0
        if p1 != p2:
            a = (q2 - q1) / (p2 - p1)
            c = (q4 - q3) / (p4 - p3)
            b = q1 - a * p1
            d = q3 - c * p3

            x = (d - b) / (a - c)
            y = a * x + b
        else:
            x = p1
            p4_p3 = p4 - p3
            if p4_p3 == 0:
                y = 0
            else:
                y = q3 + (x - p3) * (q4 - q3) / p4_p3

        return QtCore.QPointF(x, y)

    def colorFromPoint(self, p):
        # Find the outer radius of the hue gradient.
        outer_radius_width = (self.contentsRect().width() - 1) / 2
        outer_radius_height = (self.contentsRect().width() - 1) / 2
        if outer_radius_height < outer_radius_width:
            outerRadius = outer_radius_height
        else:
            outerRadius = outer_radius_width

        # Find the center coordinates
        cx = float(self.contentsRect().center().x())
        cy = float(self.contentsRect().center().y())

        # Find the a, b and c from their angles, the center of the rect
        # and the radius of the hue gradient donut.
        pa = QtCore.QPointF(
            cx + (math.cos(self.a) * (outerRadius - (outerRadius / 5.0))),
            cy - (math.sin(self.a) * (outerRadius - (outerRadius / 5.0)))
        )
        pb = QtCore.QPointF(
            cx + (math.cos(self.b) * (outerRadius - (outerRadius / 5.0))),
            cy - (math.sin(self.b) * (outerRadius - (outerRadius / 5.0)))
        )
        pc = QtCore.QPointF(
            cx + (math.cos(self.c) * (outerRadius - (outerRadius / 5.0))),
            cy - (math.sin(self.c) * (outerRadius - (outerRadius / 5.0)))
        )

        # Find the hue value from the angle of the 'a' point.
        angle = self.a - math.pi/2.0
        if angle < 0:
            angle += TWOPI
        hue = (360.0 * angle) / TWOPI

        # Create the color of the 'a' corner point. We know that b is
        # black and c is white.
        color = QtGui.QColor()
        color.setHsv(360 - int(math.floor(hue)), 255, 255)

        # See also drawTrigon(), which basically does exactly the same to
        # determine all colors in the trigon.
        p1 = Vertex(color, pa)
        p2 = Vertex(QtCore.Qt.black, pb)
        p3 = Vertex(QtCore.Qt.white, pc)

        # Make sure p1 is above p2, which is above p3.
        if p1.point.y() > p2.point.y():
            p1, p2 = p2, p1
        if p1.point.y() > p3.point.y():
            p1, p3 = p3, p1
        if p2.point.y() > p3.point.y():
            p2, p3 = p3, p2

        # Find the slopes of all edges in the trigon. All the three y
        # deltas here are positive because of the above sorting.
        p1p2ydist = p2.point.y() - p1.point.y()
        p1p3ydist = p3.point.y() - p1.point.y()
        p2p3ydist = p3.point.y() - p2.point.y()
        p1p2xdist = p2.point.x() - p1.point.x()
        p1p3xdist = p3.point.x() - p1.point.x()
        p2p3xdist = p3.point.x() - p2.point.x()

        # The first x delta decides wether we have a lefty or a righty
        # trigon. A lefty trigon has its tallest edge on the right hand
        # side of the trigon. The righty trigon has it on its left side.
        # This property determines wether the left or the right set of x
        # coordinates will be continuous.
        lefty = p1p2xdist < 0

        # Find whether the selector's y is in the first or second shorty,
        # counting from the top and downwards. This is used to find the
        # color at the selector point.
        firstshorty = (p.y() >= p1.point.y() and p.y() < p2.point.y())

        # From the y value of the selector's position, find the left and
        # right x values.
        leftx = None
        rightx = None
        if lefty:
            if firstshorty:
                leftx = p1.point.x()
                if (math.floor(p1p2ydist) != 0.0):
                    leftx += (p1p2xdist * (p.y() - p1.point.y())) / p1p2ydist
                else:
                    leftx = min(p1.point.x(), p2.point.x())

            else:
                leftx = p2.point.x()
                if (math.floor(p2p3ydist) != 0.0):
                    leftx += (p2p3xdist * (p.y() - p2.point.y())) / p2p3ydist
                else:
                    leftx = min(p2.point.x(), p3.point.x())

            rightx = p1.point.x()
            rightx += (p1p3xdist * (p.y() - p1.point.y())) / p1p3ydist
        else:
            leftx = p1.point.x()
            leftx += (p1p3xdist * (p.y() - p1.point.y())) / p1p3ydist

            if firstshorty:
                rightx = p1.point.x()
                if math.floor(p1p2ydist) != 0.0:
                    rightx += (p1p2xdist * (p.y() - p1.point.y())) / p1p2ydist
                else:
                    rightx = max(p1.point.x(), p2.point.x())

            else:
                rightx = p2.point.x()
                if math.floor(p2p3ydist) != 0.0:
                    rightx += (p2p3xdist * (p.y() - p2.point.y())) / p2p3ydist
                else:
                    rightx = max(p2.point.x(), p3.point.x())

        # Find the r,g,b values of the points on the trigon's edges that
        # are to the left and right of the selector.
        rshort = 0
        gshort = 0
        bshort = 0
        rlong = 0
        glong = 0
        blong = 0
        if firstshorty:
            if math.floor(p1p2ydist) != 0.0:
                rshort  = p2.color.r * (p.y() - p1.point.y()) / p1p2ydist
                gshort  = p2.color.g * (p.y() - p1.point.y()) / p1p2ydist
                bshort  = p2.color.b * (p.y() - p1.point.y()) / p1p2ydist
                rshort += p1.color.r * (p2.point.y() - p.y()) / p1p2ydist
                gshort += p1.color.g * (p2.point.y() - p.y()) / p1p2ydist
                bshort += p1.color.b * (p2.point.y() - p.y()) / p1p2ydist
            else:
                if lefty:
                    if p1.point.x() <= p2.point.x():
                        rshort  = p1.color.r
                        gshort  = p1.color.g
                        bshort  = p1.color.b
                    else:
                        rshort  = p2.color.r
                        gshort  = p2.color.g
                        bshort  = p2.color.b

                else:
                    if p1.point.x() > p2.point.x():
                        rshort  = p1.color.r
                        gshort  = p1.color.g
                        bshort  = p1.color.b
                    else:
                        rshort  = p2.color.r
                        gshort  = p2.color.g
                        bshort  = p2.color.b

        else:
            if math.floor(p2p3ydist) != 0.0:
                rshort  = p3.color.r * (p.y() - p2.point.y()) / p2p3ydist
                gshort  = p3.color.g * (p.y() - p2.point.y()) / p2p3ydist
                bshort  = p3.color.b * (p.y() - p2.point.y()) / p2p3ydist
                rshort += p2.color.r * (p3.point.y() - p.y()) / p2p3ydist
                gshort += p2.color.g * (p3.point.y() - p.y()) / p2p3ydist
                bshort += p2.color.b * (p3.point.y() - p.y()) / p2p3ydist
            else:
                if lefty:
                    if p2.point.x() <= p3.point.x():
                        rshort  = p2.color.r
                        gshort  = p2.color.g
                        bshort  = p2.color.b
                    else:
                        rshort  = p3.color.r
                        gshort  = p3.color.g
                        bshort  = p3.color.b

                else:
                    if p2.point.x() > p3.point.x():
                        rshort  = p2.color.r
                        gshort  = p2.color.g
                        bshort  = p2.color.b
                    else:
                        rshort  = p3.color.r
                        gshort  = p3.color.g
                        bshort  = p3.color.b

        # p1p3ydist is never 0
        rlong  = p3.color.r * (p.y() - p1.point.y()) / p1p3ydist
        glong  = p3.color.g * (p.y() - p1.point.y()) / p1p3ydist
        blong  = p3.color.b * (p.y() - p1.point.y()) / p1p3ydist
        rlong += p1.color.r * (p3.point.y() - p.y()) / p1p3ydist
        glong += p1.color.g * (p3.point.y() - p.y()) / p1p3ydist
        blong += p1.color.b * (p3.point.y() - p.y()) / p1p3ydist

        # rshort,gshort,bshort is the color on one of the shortys.
        # rlong,glong,blong is the color on the longy. So depending on
        # wether we have a lefty trigon or not, we can determine which
        # colors are on the left and right edge.
        if lefty:
            rl = rshort
            gl = gshort
            bl = bshort
            rr = rlong
            gr = glong
            br = blong
        else:
            rl = rlong
            gl = glong
            bl = blong
            rr = rshort
            gr = gshort
            br = bshort

        # Find the distance from the left x to the right x (xdist). Then
        # find the distances from the selector to each of these (saxdist
        # and saxdist2). These distances are used to find the color at
        # the selector.
        xdist = rightx - leftx
        saxdist = p.x() - leftx
        saxdist2 = xdist - saxdist

        # Now determine the r,g,b values of the selector using a linear
        # approximation.
        if xdist != 0.0:
            r = (saxdist2 * rl / xdist) + (saxdist * rr / xdist)
            g = (saxdist2 * gl / xdist) + (saxdist * gr / xdist)
            b = (saxdist2 * bl / xdist) + (saxdist * br / xdist)
        else:
            # In theory, the left and right color will be equal here. But
            # because of the loss of precision, we get an error on both
            # colors. The best approximation we can get is from adding
            # the two errors, which in theory will eliminate the error
            # but in practise will only minimize it.
            r = (rl + rr) / 2
            g = (gl + gr) / 2
            b = (bl + br) / 2

        # Now floor the color components and fit them into proper
        # boundaries. This again is to compensate for the error caused by
        # loss of precision.
        ri = int(math.floor(r))
        gi = int(math.floor(g))
        bi = int(math.floor(b))
        if ri < 0:
            ri = 0
        elif ri > 255:
            ri = 255

        if gi < 0:
            gi = 0
        elif gi > 255:
            gi = 255

        if bi < 0:
            bi = 0
        elif bi > 255:
            bi = 255

        # Voila, we have the color at the point of the selector.
        return QtGui.QColor(ri, gi, bi)

    def genBackground(self):
        innerRadius = float(self.outerRadius - self.outerRadius / 5)

        self.bg = QtGui.QImage(
            self.contentsRect().size(), QtGui.QImage.Format_RGB32
        )
        p = QtGui.QPainter(self.bg)

        p.setRenderHint(QtGui.QPainter.Antialiasing)
        p.fillRect(self.bg.rect(), self.palette().mid())

        gradient = QtGui.QConicalGradient(self.bg.rect().center(), 90)

        color = QtGui.QColor()
        idx = 0.0
        for _ in range(11):
            if QT_VERSION < 4.1:
                hue = idx * 360.0
            else:
                hue = 360.0 - (idx * 360.0)
            color.setHsv(int(hue), 255, 255)
            gradient.setColorAt(idx, color)
            idx += 0.1

        innerRadiusRect = QtCore.QRectF(
            self.bg.rect().center().x() - innerRadius,
            self.bg.rect().center().y() - innerRadius,
            innerRadius * 2 + 1, innerRadius * 2 + 1
        )
        outerRadiusRect = QtCore.QRectF(
            self.bg.rect().center().x() - self.outerRadius,
            self.bg.rect().center().y() - self.outerRadius,
            self.outerRadius * 2 + 1, self.outerRadius * 2 + 1
        )
        path = QtGui.QPainterPath()
        path.addEllipse(innerRadiusRect)
        path.addEllipse(outerRadiusRect)

        p.save()
        p.setClipPath(path)
        p.fillRect(self.bg.rect(), gradient)
        p.restore()

        penThickness = float(self.bg.width() / 400.0)
        f = 0

        for _ in range(288):
            value = int((0.5 + math.cos(((f - 1800) / 5760.0) * TWOPI) / 2) * 255.0)

            color.setHsv(
                int((f / 5760.0) * 360.0),
                int(128 + (255 - value) / 2),
                int(255 - (255 - value) / 4)
            )
            p.setPen(QtGui.QPen(color, penThickness))
            p.drawArc(innerRadiusRect, 1440 - f, 20)

            color.setHsv(
                int((f / 5760.0) * 360.0),
                int(128 + value / 2),
                int(255 - value / 4)
            )
            p.setPen(QtGui.QPen(color, penThickness))
            p.drawArc(outerRadiusRect, 2880 - 1440 - f, 20)
            f += 20
        p.end()

    @classmethod
    def qsqr(cls, a):
        return a * a

    @classmethod
    def vlen(cls, x, y):
        return math.sqrt(cls.qsqr(x) + cls.qsqr(y))

    @classmethod
    def vprod(cls, x1, y1, x2, y2):
        return x1 * x2 + y1 * y2

    def angleBetweenAngles(cls, p, a1, a2):
        if a1 > a2:
            a2 += TWOPI
            if p < math.pi:
                p += TWOPI

        return p >= a1 and p < a2

    def pointAbovePoint(self, x, y, px, py, ax, ay, bx, by):
        result = False

        if math.floor(ax) > math.floor(bx):
            if math.floor(ay) < math.floor(by):
                # line is draw upright-to-downleft
                if (
                    math.floor(x) < math.floor(px)
                    or math.floor(y) < math.floor(py)
                ):
                    result = True
            elif math.floor(ay) > math.floor(by):
                # line is draw downright-to-upleft
                if (
                    math.floor(x) > math.floor(px)
                    or math.floor(y) < math.floor(py)
                ):
                    result = True
            else:
                # line is flat horizontal
                if y < ay:
                    result = True

        elif math.floor(ax) < math.floor(bx):
            if math.floor(ay) < math.floor(by):
                # line is draw upleft-to-downright
                if (
                    math.floor(x) < math.floor(px)
                    or math.floor(y) > math.floor(py)
                ):
                    result = True
            elif math.floor(ay) > math.floor(by):
                # line is draw downleft-to-upright
                if (
                    math.floor(x) > math.floor(px)
                    or math.floor(y) > math.floor(py)
                ):
                    result = True
            else:
                # line is flat horizontal
                if y > ay:
                    result = True

        else:
            # line is vertical
            if math.floor(ay) < math.floor(by):
                if (x < ax):
                    result = True
            elif math.floor(ay) > math.floor(by):
                if x > ax:
                    result = True
            else:
                if not (x == ax and y == ay):
                    result = True

        return result

    def pointInLine(cls, x, y, ax, ay, bx, by):
        if ax > bx:
            if ay < by:
                # line is draw upright-to-downleft

                # if (x,y) is in on or above the upper right point,
                # return -1.
                if y <= ay and x >= ax:
                    return -1

                # if (x,y) is in on or below the lower left point,
                # return 1.
                if y >= by and x <= bx:
                    return 1
            else:
                # line is draw downright-to-upleft

                # If the line is flat, only use the x coordinate.
                if math.floor(ay) == math.floor(by):
                    # if (x is to the right of the rightmost point,
                    # return -1. otherwise if x is to the left of the
                    # leftmost point, return 1.
                    if x >= ax:
                        return -1
                    elif x <= bx:
                        return 1
                else:
                    # if (x,y) is on or below the lower right point,
                    # return -1.
                    if y >= ay and x >= ax:
                        return -1

                    # if (x,y) is on or above the upper left point, return 1.
                    if y <= by and x <= bx:
                        return 1
        else:
            if ay < by:
                # line is draw upleft-to-downright

                # If (x,y) is on or above the upper left point, return -1.
                if y <= ay and x <= ax:
                    return -1

                # If (x,y) is on or below the lower right point, return 1.
                if y >= by and x >= bx:
                    return 1
            else:
                # line is draw downleft-to-upright

                # If the line is flat, only use the x coordinate.
                if math.floor(ay) == math.floor(by):
                    if x <= ax:
                        return -1
                    elif x >= bx:
                        return 1
                else:
                    # If (x,y) is on or below the lower left point, return -1.
                    if y >= ay and x <= ax:
                        return -1

                    # If (x,y) is on or above the upper right point, return 1.
                    if y <= by and x >= bx:
                        return 1

        # No tests proved that (x,y) was outside [(ax,ay),(bx,by)], so we
        # assume it's inside the line's bounds.
        return 0

    def movePointToTriangle(self, x, y, a, b, c):
        # Let v1A be the vector from (x,y) to a.
        # Let v2A be the vector from a to b.
        # Find the angle alphaA between v1A and v2A.
        v1xA = x - a.point.x()
        v1yA = y - a.point.y()
        v2xA = b.point.x() - a.point.x()
        v2yA = b.point.y() - a.point.y()
        vpA = self.vprod(v1xA, v1yA, v2xA, v2yA)
        cosA = vpA / (self.vlen(v1xA, v1yA) * self.vlen(v2xA, v2yA))
        alphaA = math.acos(cosA)

        # Let v1B be the vector from x to b.
        # Let v2B be the vector from b to c.
        v1xB = x - b.point.x()
        v1yB = y - b.point.y()
        v2xB = c.point.x() - b.point.x()
        v2yB = c.point.y() - b.point.y()
        vpB = self.vprod(v1xB, v1yB, v2xB, v2yB)
        cosB = vpB / (self.vlen(v1xB, v1yB) * self.vlen(v2xB, v2yB))
        alphaB = math.acos(cosB)

        # Let v1C be the vector from x to c.
        # Let v2C be the vector from c back to a.
        v1xC = x - c.point.x()
        v1yC = y - c.point.y()
        v2xC = a.point.x() - c.point.x()
        v2yC = a.point.y() - c.point.y()
        vpC = self.vprod(v1xC, v1yC, v2xC, v2yC)
        cosC = vpC / (self.vlen(v1xC, v1yC) * self.vlen(v2xC, v2yC))
        alphaC = math.acos(cosC)

        # Find the radian angles between the (1,0) vector and the points
        # A, B, C and (x,y). Use this information to determine which of
        # the edges we should project (x,y) onto.
        angleA = self.angleAt(a.point, self.contentsRect())
        angleB = self.angleAt(b.point, self.contentsRect())
        angleC = self.angleAt(c.point, self.contentsRect())
        angleP = self.angleAt(QtCore.QPointF(x, y), self.contentsRect())

        # If (x,y) is in the a-b area, project onto the a-b vector.
        if self.angleBetweenAngles(angleP, angleA, angleB):
            # Find the distance from (x,y) to a. Then use the slope of
            # the a-b vector with this distance and the angle between a-b
            # and a-(x,y) to determine the point of intersection of the
            # perpendicular projection from (x,y) onto a-b.
            pdist = math.sqrt(
                self.qsqr(x - a.point.x()) + self.qsqr(y - a.point.y())
            )

            # the length of all edges is always > 0
            p0x = (
                a.point.x()
                + ((b.point.x() - a.point.x()) / self.vlen(v2xB, v2yB))
                * math.cos(alphaA) * pdist
            )
            p0y = (
                a.point.y()
                + ((b.point.y() - a.point.y()) / self.vlen(v2xB, v2yB))
                * math.cos(alphaA) * pdist
            )

            # If (x,y) is above the a-b line, which basically means it's
            # outside the triangle, then return its projection onto a-b.
            if self.pointAbovePoint(
                x, y,
                p0x, p0y,
                a.point.x(), a.point.y(),
                b.point.x(), b.point.y()
            ):
                # If the projection is "outside" a, return a. If it is
                # outside b, return b. Otherwise return the projection.
                n = self.pointInLine(
                    p0x, p0y,
                    a.point.x(), a.point.y(),
                    b.point.x(), b.point.y()
                )
                if n < 0:
                    return a.point
                elif n > 0:
                    return b.point

                return QtCore.QPointF(p0x, p0y)

        elif self.angleBetweenAngles(angleP, angleB, angleC):
            # If (x,y) is in the b-c area, project onto the b-c vector.
            pdist = math.sqrt(
                self.qsqr(x - b.point.x()) + self.qsqr(y - b.point.y())
            )

            # the length of all edges is always > 0
            p0x = (
                b.point.x()
                + ((c.point.x() - b.point.x()) / self.vlen(v2xC, v2yC))
                * math.cos(alphaB) * pdist
            )
            p0y = (
                b.point.y()
                + ((c.point.y() - b.point.y()) / self.vlen(v2xC, v2yC))
                * math.cos(alphaB)
                * pdist
            )

            if self.pointAbovePoint(
                x, y,
                p0x, p0y,
                b.point.x(), b.point.y(),
                c.point.x(), c.point.y()
            ):
                n = self.pointInLine(
                    p0x, p0y,
                    b.point.x(), b.point.y(),
                    c.point.x(), c.point.y()
                )
                if n < 0:
                    return b.point
                elif n > 0:
                    return c.point
                return QtCore.QPointF(p0x, p0y)

        elif self.angleBetweenAngles(angleP, angleC, angleA):
            # If (x,y) is in the c-a area, project onto the c-a vector.
            pdist = math.sqrt(
                self.qsqr(x - c.point.x()) + self.qsqr(y - c.point.y())
            )

            # the length of all edges is always > 0
            p0x = (
                c.point.x()
                + ((a.point.x() - c.point.x()) / self.vlen(v2xA, v2yA))
                * math.cos(alphaC)
                * pdist
            )
            p0y = (
                c.point.y()
                + ((a.point.y() - c.point.y()) / self.vlen(v2xA, v2yA))
                * math.cos(alphaC) * pdist
            )

            if self.pointAbovePoint(
                x, y,
                p0x, p0y,
                c.point.x(), c.point.y(),
                a.point.x(), a.point.y()
            ):
                n = self.pointInLine(
                    p0x, p0y,
                    c.point.x(), c.point.y(),
                    a.point.x(), a.point.y()
                )
                if n < 0:
                    return c.point
                elif n > 0:
                    return a.point
                return QtCore.QPointF(p0x, p0y)

        # (x,y) is inside the triangle (inside a-b, b-c and a-c).
        return QtCore.QPointF(x, y)
