import os
from utils.photoneo.photoneo_config_editor import open_photoneo_config
from utils.mechmind.mechmind_config import open_mechmind_config
class ConfigurationManager:
  def __init__(self, camera_info):
    self.camera_info = camera_info.split(" - ")
    self.config_window = None  

  def load(self):
    if ("Photoneo" in self.camera_info):
      self.config_window = open_photoneo_config(self)
    if ("MechMind" in self.camera_info):
      self.config_window = open_mechmind_config(camera_ip=self.camera_info[2])

    