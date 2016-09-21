# -*- coding: utf-8 -*-

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
global search_term
# search_term = "boop"

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

def gainFocus(note, field):
    global search_term
    global currentNote
    global mediaField
    # Sets the search term to the field you're on
    # Note: does not work with newly added fields until restart
    search_term = note.fields[field]
    currentNote = note
    mediaField = field

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


""" Edits Anki's menu to include adding a note image
"""

# import the main window object (mw) from ankiqt
from aqt import mw
# import the "show info" tool from utils.py
from aqt.utils import showInfo
# import all of the Qt GUI library
from aqt.qt import *

try:
    mw.edit_media_submenu.addSeparator()
except AttributeError:
    mw.edit_media_submenu = QMenu(u"&Media", mw)
    mw.form.menuEdit.addSeparator()
    mw.form.menuEdit.addMenu(mw.edit_media_submenu)

# create a new menu item
mw.images_search_action = QAction(mw)
mw.images_search_action.setText(u"Note image")
# mw.note_download_action.setToolTip(
#     "Download images for all image fields on this note.")

# set it to call testFunction when it's clicked
mw.connect(mw.images_search_action, SIGNAL("triggered()"), download_image_for_note)

mw.edit_media_submenu.addAction(mw.images_search_action)

addHook("editFocusGained", gainFocus)