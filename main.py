# -*- coding: utf-8 -*-
import urllib
import urllib2
import json

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

#more imports
from anki.hooks import addHook
from aqt.editor import Editor


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

# FieldData class for English data modeled from download_audio plugin
class FieldData(object):

    #constructor
    def __init__(self, w_field, word):
        self.word_field_name = w_field
        # Take word from aqt/browser.py
        self.word = word.replace(u'<br>', u' ')
        self.word = self.word.replace(u'<br />', u' ')

    @property
    def empty(self):
        return not self.word

class imagesDialog(QDialog):
    def __init__(self):
        super(imagesDialog, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle(_(u'Anki – Download images'))
        self.setWindowIcon(QIcon(":/icons/anki.png"))
        view = Browser()

        search_term = "strawberry"#self.word
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


    def setupButtons(self):
        open_button = self._addButton("image_dialog", lambda self=self: review_entries(),
                    text=u"img\u0336", tip="ImageDialog (Ctrl+i)", key="Ctrl+i")

    addHook("setupEditorButtons", setupButtons)
