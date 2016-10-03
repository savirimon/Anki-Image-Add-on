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



def initialize_canvas():
    paintTool = Canvas()
    paintTool.exec_()
    #update GUI here

def gainFocus(note, field):
    global search_term
    global currentNote
    global mediaField
    # Sets the search term to the field you're on
    # Note: does not work with newly added fields until restart
    search_term = note.fields[field]
    currentNote = note
    mediaField = field

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
        self.drawMode = "point"
        self.path = QPainterPath()
        self.setWindowFlags(Qt.WindowCloseButtonHint)

    def initUI(self):
        self.setGeometry(300, 300, 280, 170)
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