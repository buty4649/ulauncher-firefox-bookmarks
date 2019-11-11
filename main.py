import os
import sqlite3
import configparser
import shutil
import tempfile

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction


class FirefoxBookmark(Extension):

    def __init__(self):
        super(FirefoxBookmark, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

  MAX_ITEM_COUNT = 8
  BOOKMARK_QUERY = """
SELECT
 distinct moz_places.id, moz_bookmarks.title, moz_places.url, moz_places.url_hash from moz_places
 INNER JOIN moz_bookmarks ON moz_places.id = moz_bookmarks.fk
WHERE
  moz_places.title LIKE ?
  OR
  moz_places.url LIKE ?
LIMIT ?
"""

  def __init__(self):
    self.db_path = os.path.join(self.get_profile_path(), "places.sqlite")

  def on_event(self, event, extension):
    keyword = event.get_argument()
    items = []
    for bookmark in self.get_bookmark_items(keyword):
      (id, title, url, hash) = bookmark
      items.append(ExtensionResultItem(icon='images/icon.png',
                                        name=title,
                                        description=url,
                                        on_enter=OpenUrlAction(url)))

    return RenderResultListAction(items)

  def on_close(self, event, extension):
    pass

  def get_profile_path(self):
    base_path = os.path.join(os.environ['HOME'], '.mozilla/firefox/')

    profile = configparser.ConfigParser()
    profile.read(os.path.join(base_path, "profiles.ini"))
    profile_path = profile.get("Profile0", "Path")

    return os.path.join(base_path, profile_path)

  def get_bookmark_items(self, keyword):
    if keyword is None:
      search_keyword = "%"
    else:
      kw = keyword.replace("%", "\\$%").replace("_", "\\$_")
      search_keyword = "%%%s%%" % kw

    with tempfile.TemporaryDirectory() as tmp:
      temp_db_path = os.path.join(tmp, "places.sqlite")
      shutil.copyfile(self.db_path, temp_db_path)

      db = sqlite3.connect(temp_db_path)
      result = db.execute(self.BOOKMARK_QUERY, [search_keyword, search_keyword, self.MAX_ITEM_COUNT])
      db.close

    return result

if __name__ == '__main__':
    FirefoxBookmark().run()

