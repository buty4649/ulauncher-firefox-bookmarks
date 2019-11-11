import os
import sqlite3
import configparser

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

  def __init__(self):
    db_path = os.path.join(self.get_profile_path(), "places.sqlite")
    self.db = sqlite3.connect(db_path)

  def on_event(self, event, extension):
    items = []
    sql = """
select distinct moz_places.id, moz_bookmarks.title, moz_places.url, moz_places.url_hash from moz_places inner join
 moz_bookmarks on moz_places.id = moz_bookmarks.fk
WHERE
  moz_places.title LIKE ?
  or 
  moz_places.url LIKE ?
LIMIT ?
"""
    argument = event.get_argument().replace("%", "\\$%").replace("_", "\\$_") if event.get_argument() else ""
    search_term = ''.join(["%", argument, "%"])
    for row in self.db.execute(sql, [search_term, search_term, self.MAX_ITEM_COUNT]):
      (id, title, url, hash) = row
      items.append(ExtensionResultItem(icon='images/icon.png',
                                        name=title,
                                        description=url,
                                        on_enter=OpenUrlAction(url)))

    return RenderResultListAction(items)

  def on_close(self, event, extension):
    self.db.close()

  def get_profile_path(self):
    base_path = os.path.join(os.environ['HOME'], '.mozilla/firefox/')

    profile = configparser.ConfigParser()
    profile.read(os.path.join(base_path, "profiles.ini"))
    profile_path = profile.get("Profile0", "Path")

    return os.path.join(base_path, profile_path)

if __name__ == '__main__':
    FirefoxBookmark().run()

