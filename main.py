import os
import sqlite3
import shutil
import tempfile
import firefox_profile

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.OpenUrlAction import OpenUrlAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

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
    self.ffprofile = firefox_profile.FirefoxProfile()

  def on_event(self, event, extension):
    keyword = event.get_argument()
    profile = extension.preferences['profile']
    profile_path = self.ffprofile.get_profile_path(profile)

    if profile_path is None:
      item = ExtensionResultItem(
        icon='images/icon.png',
        name="Profile is not found",
        description="The specified profile '%s' does not exist." % profile,
        on_enter=DoNothingAction()
      )
      return RenderResultListAction([item])

    items = []
    for bookmark in self.get_bookmark_items(keyword, profile_path):
      (_, title, url, _) = bookmark
      items.append(ExtensionResultItem(icon='images/icon.png',
                                        name=title,
                                        description=url,
                                        on_enter=OpenUrlAction(url)))

    return RenderResultListAction(items)

  def on_close(self, event, extension):
    pass

  def get_bookmark_items(self, keyword, profile_path):
    if keyword is None:
      search_keyword = "%"
    else:
      kw = keyword.replace("%", "\\$%").replace("_", "\\$_")
      search_keyword = "%%%s%%" % kw

    with tempfile.TemporaryDirectory() as tmp:
      temp_db_path = os.path.join(tmp, "places.sqlite")
      db_path = os.path.join(profile_path, "places.sqlite")
      shutil.copyfile(db_path, temp_db_path)

      db = sqlite3.connect(temp_db_path)
      result = db.execute(self.BOOKMARK_QUERY, [search_keyword, search_keyword, self.MAX_ITEM_COUNT])
      db.close

    return result

if __name__ == '__main__':
    FirefoxBookmark().run()
