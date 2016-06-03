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



def review_entries():
    review_images = imagesDialog()
    if not review_images.exec_():
        raise RuntimeError('User cancel')

def download_image_for_note():
    review_entries()

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
        self.setWindowTitle(_(u'Anki – Download images'))
        self.setWindowIcon(QIcon(":/icons/anki.png"))
        view = Browser()
        search_term = "fruit"
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


def bing_search(query, search_type):
    #search_type: Web, Image, News, Video
    key= 'pKeY477b24auIf1Cms84RpwkAnzHyT2EWOfuzmQNQdg'
    query = urllib.quote(query)
    # create credential for authentication
    user_agent = 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; FDM; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 1.1.4322)'
    credentials = (':%s' % key).encode('base64')[:-1]
    auth = 'Basic %s' % credentials
    url = 'https://api.datamarket.azure.com/Data.ashx/Bing/Search/'+search_type+'?Query=%27'+query+'%27&$top=5&$format=json'
    request = urllib2.Request(url)
    request.add_header('Authorization', auth)
    request.add_header('User-Agent', user_agent)
    request_opener = urllib2.build_opener()
    response = request_opener.open(request)
    response_data = response.read()
    json_result = json.loads(response_data)
    result_list = json_result['d']['results']
    print result_list
    return result_list


try:
    mw.edit_media_submenu.addSeparator()
except AttributeError:
    mw.edit_media_submenu = QMenu(u"&Media", mw)
    mw.form.menuEdit.addSeparator()
    mw.form.menuEdit.addMenu(mw.edit_media_submenu)

# create a new menu item
mw.images_search_action = QAction(mw)
mw.images_search_action.setText(u"Note image")
mw.note_download_action.setToolTip(
    "Download images for all image fields on this note.")

# set it to call testFunction when it's clicked
mw.connect(mw.images_search_action, SIGNAL("triggered()"), download_image_for_note)

mw.edit_media_submenu.addAction(mw.images_search_action)
