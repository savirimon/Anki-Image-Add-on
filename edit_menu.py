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
