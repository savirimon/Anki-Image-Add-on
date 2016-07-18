# -*- coding: utf-8 -*-
import urllib
import urllib2
import json

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

#global vars
search_term = "boop"

#Canvas class for drawing new study images
class Canvas(QWidget):
    def __init__(self):
        super(Canvas, self).__init__()
        self.initUI()
        self.prevPoint = QPoint()
        self.drawing = False
        self.color = Qt.black

    def initUI(self):
        self.text = u'\u041b\u0435\u0432 \u041d\u0438\u043a\u043e\u043b\u0430\
            \u0435\u0432\u0438\u0447 \u0422\u043e\u043b\u0441\u0442\u043e\u0439: \n\
            \u0410\u043d\u043d\u0430 \u041a\u0430\u0440\u0435\u043d\u0438\u043d\u0430'

        self.setGeometry(300, 300, 280, 170)
        self.setWindowTitle('Draw Reference Image')
        self.show()

    def paintEvent(self, event):
        painter = QPainter();
        painter.begin(self)
        self.drawText(event, painter)
        painter.end()

    def drawText(self, event, painter):
        painter.setPen()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.lastPoint = event.pos()
            self.drawing = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.drawing:
            self.drawLineTo(event.pos())
            self.drawing = false

    def drawLine(self, currPoint):
        painter = QPainter(self.image)
        painter.setPen(QPen(self.color, self.penWidth, Qt.SolidLine, Qt.RoundCap,
            Qt.RoundJoin))
        painter.drawLine(self.prevPoint, currPoint)
        self.update()
        self.prevPoint = QPoint(currPoint)     

def initialize_canvas():
    paintTool = Canvas()
    paintTool.show()

def review_entries():
    review_images = imagesDialog()
    if not review_images.exec_():
        raise RuntimeError('User cancel')

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

    def setupSearchBrowserButton(self):
        open_button = self._addButton("imagesDialog", lambda self=self: review_entries(),
                    text=u"img\u0336", tip="ImageDialog (Ctrl+i)", key="Ctrl+i")

    def setupDrawingCanvasButton(self):
        canvas_button = self._addButton("Canvas", lambda self=self: initialize_canvas(),
                text=u"d\u0336", tip="Canvas (Ctrl+d)", key="Ctrl+d")

    def gainFocus(note, field):
        global search_term
        # Sets the search term to the field you're on
        # Note: does not work with newly added fields until restart
        search_term = note.fields[field]

    Editor.setupButtons = wrap(Editor.setupButtons, setupSearchBrowserButton)
    Editor.setupButtons = wrap(Editor.setupButtons, setupDrawingCanvasButton)   
    addHook("editFocusGained", gainFocus)
