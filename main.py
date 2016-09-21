# -*- coding: utf-8 -*-
import urllib
import urllib2
import json

import aqt.editor

import sys
print(sys.path)
sys.path.append(".")
print(sys.path)

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

# import web_search.py

from web_search import review_entries
from paint_tool import initialize_canvas
#

#Debugging
#import code
# code.interact(local=locals())


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
