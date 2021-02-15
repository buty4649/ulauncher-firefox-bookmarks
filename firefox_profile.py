import os
import configparser

class FirefoxProfile:

  def __init__(self):
    self.base_path = os.path.join(os.environ['HOME'], '.mozilla/firefox/')
    self.profile = configparser.ConfigParser()
    self.profile.read(os.path.join(self.base_path, "profiles.ini"))
    pass

  def get_profile_path(self, name=None):
    if name and name != "":
      profiles = self.get_all_profiles()
      if name not in profiles:
        return None
      return profiles[name]
    else:
      section = [s for s in self.profile.sections() if s.startswith("Install")][0]
      profile = self.profile[section]["Default"]
      return os.path.join(self.base_path, profile)

  def get_all_profiles(self):
    profiles = [s for s in self.profile.sections() if s.startswith("Profile")]
    result = {}
    for p in profiles:
      name = self.profile[p]["Name"]
      path = os.path.join(self.base_path, self.profile[p]["Path"])
      result[name] = path

    return result
