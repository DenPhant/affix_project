import os
from pathlib import Path
from sys import platform
from harvesters.core import Harvester
import struct
import re
import json

class PhotoneoToolControl:
  def __init__(self):
    self.config_dir = "/utils/photoneo/configs"
  def list_cameras(self):
    cti_path = os.getenv('PHOXI_CONTROL_PATH') + "/API/bin/photoneo.cti"
    with Harvester() as h:
      h.add_file(cti_path, check_existence=True, check_validity=True)
      h.update()
      devices = []
      for device in h.device_info_list:
        item = device.display_name + " - " + device.id_ + " - " + device.version + " - " + device.vendor
        devices.append(item)
      return devices
  
  def grab_def_config(self, camera_info):
    if ("MotionCam"):
      return 
      

  def find_cfg_file(folder_path, cfg_type):
    cfg_def_name = f"cfg_def_{cfg_type}.json"
    cfg_def_path = None

    for filename in os.listdir(folder_path):
      if filename.endswith(".json"):
        if filename == cfg_def_name:
          cfg_def_path = os.path.join(folder_path, filename)
        elif cfg_type in filename and filename != cfg_def_name:
          return os.path.join(folder_path, filename)

    return cfg_def_path

  def save_config(self, features, cfg_name):
    if(cfg_name is None or cfg_name == ""):
      cfg_name = "unnamed"
    #Create a JSON file
    filename = cfg_name + ".json"
    path = os.path.join(self.config_dir, filename)
    with open(path, 'w') as f:
      json.dump(self.get_config(), f, indent=2)
  

  def _snake_to_pascal(self, snake_wrd):
    return ''.join(word.capitalize() for word in snake_wrd.split('_'))

  def _pascal_to_snake(self, pascal_wrd):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', pascal_wrd)  
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)   
    return s2.lower()
  

  def get_value(self, key, features):
    try:
      
      val = getattr(features,key).value
      
      return val
    except Exception as ex:
      print(ex)

  def apply_config_to_motioncam(self, config, features):
    for section, items in config.items():
      for key, value in items.items():
        try:
          
          #feat_key = self._snake_to_pascal(key)
          #if feat_key in features:
            #features[feat_key].value = value
          self.set_nested_attr(features,key, value)
        except Exception as e:
          print(f"Warning: Failed to set {key} in {section}: {e}")
  

  def set_nested_attr(self,obj, attr_path, value):
    attrs = attr_path.split('.')
    for attr in attrs[:-1]:
        if not hasattr(obj, attr):
            setattr(obj, attr, object)
        obj = getattr(obj, attr)
    setattr(obj, attrs[-1], value)
  
  def get_nested_attr(self):
    pass