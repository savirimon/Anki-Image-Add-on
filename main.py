# -*- coding: utf-8 -*-
import urllib
import urllib2
import json

import aqt.editor

# import the main window object (mw) from ankiqt
from aqt import mw, browser, editor
# import the "show info" tool from utils.py
from aqt.utils import showInfo
from anki.utils import stripHTML
# import all of the Qt GUI library
from aqt.qt import *
from aqt.editor import Editor

#more imports
from anki.hooks import addHook, runHook, wrap
from anki.consts import MODEL_STD

#Debugging
#import code
# code.interact(local=locals())

#global vars
global search_term
search_term = "boop"


def initialize_canvas():
    paintTool = Canvas()
    paintTool.exec_()
    #update GUI here

def review_entries():
    review_images = imagesDialog()
    if not review_images.exec_():
        return
        #raise RuntimeError('User cancel')

def download_image_for_note():
    try:
        review_entries()
    except RuntimeError as rte:
        if 'cancel' in str(rte):
            # User cancelled, so close silently
            return
        else:
            #unhandled
            raise

def setupSearchBrowserButton(self):
    open_button = self._addButton("imagesDialog", lambda self=self: review_entries(),
                text=u"img\u0336", tip="ImageDialog (Ctrl+i)", key="Ctrl+i")

def setupDrawingCanvasButton(self):
    canvas_button = self._addButton("Canvas", lambda self=self: initialize_canvas(),
            text=u"d\u0336", tip="Canvas (Ctrl+d)", key="Ctrl+d")

def gainFocus(note, field):
    global search_term
    global currentNote
    global mediaField
    # Sets the search term to the field you're on
    # Note: does not work with newly added fields until restart
    search_term = note.fields[field]
    currentNote = note
    mediaField = field


Editor.setupButtons = wrap(Editor.setupButtons, setupSearchBrowserButton)
Editor.setupButtons = wrap(Editor.setupButtons, setupDrawingCanvasButton)
addHook("editFocusGained", gainFocus)



####### Custom Classes ######


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

    def initUI(self):
        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Draw Reference Image')
        self.show()

    #TODO: MAKE IT SO IT DISPLAYS CORRECT IMAGE WHEN THERE'S AN EXISTING IMAGE
    def saveImage(self):
        # save image to media folder 
        pixels = QPixmap.grabWidget(self)
        fileName = 'test1.jpg'
        pixels.save(fileName, 'jpg')
        # send to card in first empty field
        data = data = u'<img src="%s">' % fileName

        for(name, value) in currentNote.items():
            if name == 'Back':
                currentNote[name] = value + data
        currentNote.flush()
        mw.noteChanged(currentNote.id)
        mw.reset()

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

class Browser(QWebView):

    def __init__(self):
        QWebView.__init__(self)
        self.loadFinished.connect(self._result_available)

    def _result_available(self, ok):
        frame = self.page().mainFrame()
        print unicode(frame.toHtml()).encode('utf-8')

class imagesDialog(QDialog):
    def __init__(self):
        super(imagesDialog, self).__init__()
        self.initUI()

    def initUI(self):
        global search_term
        search_term = str(search_term)
        # runHook("editFocusGained", self.note, field)
        self.setWindowTitle(_(u'Anki – Download images'))
        self.setWindowIcon(QIcon(":/icons/anki.png"))
        # mw.editor.saveNow()

        view = Browser()
        # search_term = stripHTML(search_term)
        search_term = search_term.replace(u'<br>', u' ')
        search_term = search_term.replace(u'<br />', u' ')
        # search_term = search_term.replace([u'])
        #search_term = Editor.currentField #self.word
        url = "https://www.google.com/search?tbm=isch&q=" + search_term + "&oq=" + search_term
        view.load(QUrl(url))

        outer_layout = QVBoxLayout()
        self.setLayout(outer_layout)

        outer_layout.addWidget(view)


    # def mouseReleaseEvent(self, event):
    #     self.drawing = False
    #     self.update()

    # def mouseMoveEvent(self, event):
    #     if self.drawing:
    #         self.points.append(event.pos())
    #         self.update()

    # def keyPressEvent(self, event):
    #     self.saveImage()

    # def dragEnterEvent(self, event):
        # if(event.mimeData().hasImage()):


        # query = "sunshine"
        # search_results = bing_search(query, 'Image')

        # # Remplazar por QTreeWidget or QTableWidget
        # list = QListWidget(self)
        # #list.setDragDropMode(QAbstractItemView.NoDragDrop)
        # list.setUniformItemSizes(True)
        # list.setViewMode(1) # Set to icon view mode
        # list.setIconSize(QSize(200,200))
        # for result in search_results:
        #     item = QListWidgetItem()

        #     item.setText(result['Title'])
        #     image_data = urllib2.urlopen(result['Thumbnail']['MediaUrl']).read()
        #     qimage = QImage()
        #     qimage.loadFromData(image_data)

        #     item.setIcon(QIcon(QPixmap(qimage)))

        #     list.addItem(item)
        # outer_layout.addWidget(list)

