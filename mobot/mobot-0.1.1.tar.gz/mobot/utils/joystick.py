from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class Joystick(QWidget):
    pose = pyqtSignal(float,float)
    def __init__(self, parent=None):
        super(Joystick, self).__init__(parent)
        self.setMinimumSize(250, 250)
        self.movingOffset = QPointF(0, 0)
        self.grabCenter = False
        self.__maxDistance = 100

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawEllipse(self._bound())
        painter.setBrush(QBrush(Qt.black, Qt.SolidPattern))
        painter.drawEllipse(self._centerEllipse())

    def _bound(self):
        bounds = QRectF(-self.__maxDistance, -self.__maxDistance, self.__maxDistance * 2, self.__maxDistance * 2)
        return bounds.translated(self._center())

    def _centerEllipse(self):
        if self.grabCenter:
            return QRectF(-20, -20, 40, 40).translated(self.movingOffset)
        return QRectF(-20, -20, 40, 40).translated(self._center())

    def _center(self):
        return QPointF(self.width()/2, self.height()/2)

    def _boundJoystick(self, point):
        limitLine = QLineF(self._center(), point)
        if (limitLine.length() > self.__maxDistance):
            limitLine.setLength(self.__maxDistance)
        return limitLine.p2()

    def emit(self):
        offset = self.movingOffset - self._center() 
        self.pose.emit(offset.x(), offset.y())

    def mousePressEvent(self, event):
        self.grabCenter = self._bound().contains(event.pos())
        if self.grabCenter:
            self.movingOffset = self._boundJoystick(event.pos())
            self.update()
            self.emit()
        return super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        if self.grabCenter:
            self.grabCenter = False
            self.movingOffset = self._center()
            self.update()
            self.emit()

    def mouseMoveEvent(self, event):
        if self.grabCenter:
            self.movingOffset = self._boundJoystick(event.pos())
            self.update()
            self.emit()
