# -*- coding: utf-8 -*-

# import the main window object (mw) from ankiqt
from aqt import mw, browser
# import the "show info" tool from utils.py
from aqt.utils import showInfo
from anki.utils import stripHTML
# import all of the Qt GUI library
from aqt.qt import *

#more imports
from anki.hooks import addHook, runHook, wrap
from anki.consts import MODEL_STD


def gainFocus(note, field):
    global search_term
    global currentNote
    global mediaField
    # Sets the search term to the field you're on
    # Note: does not work with newly added fields until restart
    search_term = note.fields[field]
    currentNote = note
    mediaField = field


def initialize_canvas():
    paintTool = PaintWindow()
    paintTool.exec_()
    #update GUI here

# Layout definition from PyQt example

class ItemWrapper(object):
    def __init__(self, i, p):
        self.item = i
        self.position = p


class BorderLayout(QLayout):
    West, North, South, East, Center = range(5)
    MinimumSize, SizeHint = range(2)

    def __init__(self, parent=None, margin=0, spacing=-1):
        super(BorderLayout, self).__init__(parent)

        self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)
        self.list = []

    def __del__(self):
        l = self.takeAt(0)
        while l:
            l = self.takeAt(0)

    def addItem(self, item):
        self.add(item, BorderLayout.West)

    def addWidget(self, widget, position):
        self.add(QWidgetItem(widget), position)

    def expandingDirections(self):
        return Qt.Horizontal | Qt.Vertical

    def hasHeightForWidth(self):
        return False

    def count(self):
        return len(self.list)

    def itemAt(self, index):
        if index < len(self.list):
            return self.list[index].item

        return None

    def minimumSize(self):
        return self.calculateSize(BorderLayout.MinimumSize)

    def setGeometry(self, rect):
        center = None
        eastWidth = 0
        westWidth = 0
        northHeight = 0
        southHeight = 0
        centerHeight = 0

        super(BorderLayout, self).setGeometry(rect)

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == BorderLayout.North:
                item.setGeometry(QRect(rect.x(), northHeight,
                        rect.width(), item.sizeHint().height()))

                northHeight += item.geometry().height() + self.spacing()

            elif position == BorderLayout.South:
                item.setGeometry(QRect(item.geometry().x(),
                        item.geometry().y(), rect.width(),
                        item.sizeHint().height()))

                southHeight += item.geometry().height() + self.spacing()

                item.setGeometry(QRect(rect.x(),
                        rect.y() + rect.height() - southHeight + self.spacing(),
                        item.geometry().width(), item.geometry().height()))

            elif position == BorderLayout.Center:
                center = wrapper

        centerHeight = rect.height() - northHeight - southHeight

        for wrapper in self.list:
            item = wrapper.item
            position = wrapper.position

            if position == BorderLayout.West:
                item.setGeometry(QRect(rect.x() + westWidth,
                        northHeight, item.sizeHint().width(), centerHeight))

                westWidth += item.geometry().width() + self.spacing()

            elif position == BorderLayout.East:
                item.setGeometry(QRect(item.geometry().x(),
                        item.geometry().y(), item.sizeHint().width(),
                        centerHeight))

                eastWidth += item.geometry().width() + self.spacing()

                item.setGeometry(QRect(rect.x() + rect.width() - eastWidth + self.spacing(),
                        northHeight, item.geometry().width(),
                        item.geometry().height()))

        if center:
            center.item.setGeometry(QRect(westWidth, northHeight,
                    rect.width() - eastWidth - westWidth, centerHeight))

    def sizeHint(self):
        return self.calculateSize(BorderLayout.SizeHint)

    def takeAt(self, index):
        if index >= 0 and index < len(self.list):
            layoutStruct = self.list.pop(index)
            return layoutStruct.item

        return None

    def add(self, item, position):
        self.list.append(ItemWrapper(item, position))

    def calculateSize(self, sizeType):
        totalSize = QSize()

        for wrapper in self.list:
            position = wrapper.position
            itemSize = QSize()

            if sizeType == BorderLayout.MinimumSize:
                itemSize = wrapper.item.minimumSize()
            else: # sizeType == BorderLayout.SizeHint
                itemSize = wrapper.item.sizeHint()

            if position in (BorderLayout.North, BorderLayout.South, BorderLayout.Center):
                totalSize.setHeight(totalSize.height() + itemSize.height())

            if position in (BorderLayout.West, BorderLayout.East, BorderLayout.Center):
                totalSize.setWidth(totalSize.width() + itemSize.width())

        return totalSize


#Canvas class for drawing new study images
class Canvas(QDialog):

    def __init__(self):
        super(Canvas, self).__init__()
        self.initUI()
        self.penWidth = 3
        self.drawing = False
        self.color = Qt.black
        self.points = []
        self.lines = []
        self.rects = []
        self.circles = []
        self.preview = []
        self.start = None
        self.end = None
        self.drawMode = "line"
        self.path = QPainterPath()

    def initUI(self):
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(300, 100, 800, 800)
        self.setWindowTitle('Draw Reference Image')
        self.show()

    def paintEvent(self, event = None):
        print("Paint Event")
        painter = QPainter();
        painter.begin(self)
        painter.setPen(QPen(self.color, self.penWidth, Qt.SolidLine, Qt.RoundCap,
            Qt.RoundJoin))

        if self.drawMode == "point" and self.end != None:
            painter.drawEllipse(self.end.x(), self.end.y(), 1, 1)
        else:
            if self.start != None and self.end != None:
                if self.drawMode == "line":
                    painter.drawLine(self.start.x(), self.start.y(), self.end.x(), self.end.y())
                elif self.drawMode == "rect":
                    painter.drawRect(self.start.x(), self.start.y(), self.end.x() - self.start.x(), self.end.y() - self.start.y())
                elif self.drawMode == "ellipse":
                    painter.drawRect(self.start.x(), self.start.y(), self.end.x() - self.start.x(), self.end.y() - self.start.y())
        painter.drawPath(self.path)
        # for pt in self.preview:
        #     painter.drawPoint(pt)

        painter.end()

    def mousePressEvent(self, event):
        print("Pressed")
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.start = event.pos()
            self.path.moveTo(self.start)
            self.update()

    def mouseReleaseEvent(self, event):
        if self.drawMode == "point":
            self.path.addEllipse(event.pos().x(), event.pos().y(), 1, 1)

        if self.start != None and self.end != None:
            if self.drawMode == "line":
                self.path.lineTo(self.end.x(), self.end.y())
            elif self.drawMode == "rect":
                self.path.addRect(self.start.x(), self.start.y(),
                    self.end.x() - self.start.x(),
                    self.end.y() - self.start.y())
            elif self.drawMode == "ellipse":
                self.path.addEllipse(self.start.x(), self.start.y(),
                    self.end.x() - self.start.x(),
                    self.end.y() - self.start.y())
            self.update()

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end = event.pos()
            self.update()

    def setDrawMode(self, mode):
        self.drawMode = mode

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.saveImage()
            self.done(1)
        elif event.key() == Qt.Key_L:
            self.drawMode = "line"
        elif event.key() == Qt.Key_P:
            self.drawMode = "point"
        elif event.key() == Qt.Key_R:
            self.drawMode = "rect"
        elif event.key() == Qt.Key_E:
            self.drawMode = "ellipse"
        elif event.key() == Qt.Key_1:
            self.color = Qt.black;
        elif event.key() == Qt.Key_2:
            self.color = Qt.red;


    #TODO: MAKE IT SO IT DISPLAYS CORRECT IMAGE WHEN THERE'S AN EXISTING IMAGE
    def saveImage(self):
        # save image to media folder
        pixels = QPixmap.grabWidget(self)
        fileName = 'test1.jpg'
        pixels.save(fileName, 'jpg')
        # send to card in first empty field
        data = data = u'<img src="%s">' % fileName

        global currentNote

        for(name, value) in currentNote.items():
            if name == 'Back':
                currentNote[name] = value + data
        currentNote.flush()
        mw.noteChanged(currentNote.id)
        mw.reset()

addHook("editFocusGained", gainFocus)

# Window to hold Paint Canvas
class PaintWindow(QDialog):
    def __init__(self):
        super(PaintWindow, self).__init__()

        self.canvas = Canvas()

        layout = BorderLayout()
        layout.addWidget(self.canvas, BorderLayout.Center)

        # Because BorderLayout doesn't call its super-class addWidget() it
        # doesn't take ownership of the widgets until setLayout() is called.
        # Therefore we keep a local reference to each label to prevent it being
        # garbage collected too soon.
        label_n = self.createLabel("North")
        layout.addWidget(label_n, BorderLayout.North)

        label_w = self.createLabel("West")
        self.pointButton = QToolButton()
        self.pointButton.setText("point")
        self.connect(self.pointButton, SIGNAL('clicked()'), self.setMode)
        self.pointButton.show()
        self.pointButton.setCheckable(True)
        self.paintButtons = QDialogButtonBox();
        self.paintButtons.setOrientation(Qt.Vertical)
        self.paintButtons.addButton(self.pointButton, QDialogButtonBox.ActionRole)
        self.paintButtons.show()
        # layout.addWidget(verticalButtonBox, BorderLayout.West)
        layout.addWidget(self.paintButtons, BorderLayout.West);
        layout.addWidget(label_w, BorderLayout.West)

        label_e1 = self.createLabel("East 1")
        layout.addWidget(label_e1, BorderLayout.East)

        label_e2 = self.createLabel("East 2")
        layout.addWidget(label_e2, BorderLayout.East)

        label_s = self.createLabel("South")
        layout.addWidget(label_s, BorderLayout.South)

        self.setLayout(layout)

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setGeometry(300, 100, 800, 800)
        self.setWindowTitle('Draw Reference Image')
        self.show()

    def setMode(self):
        # go through all buttons and find the one that's download
        for button in self.paintButtons.buttons():
            if button.isChecked():
                self.canvas.setDrawMode(button.text())

    def keyPressEvent(self, event):
        self.canvas.keyPressEvent(event)

        if event.key() == Qt.Key_Space:
            self.done(1)

    def mousePressEvent(self, event):
        self.canvas.mousePressEvent(event)

    def mouseMoveEvent(self, event):
        self.canvas.mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.canvas.mouseReleaseEvent(event)
        self.setMode()

    def paintEvent(self, event):
        self.canvas.paintEvent(event)

    def createLabel(self, text):
        label = QLabel(text)
        label.setFrameStyle(QFrame.Box | QFrame.Raised)
        return label
