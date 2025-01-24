import os
import json
from PyQt5.QtWidgets import QFileDialog

#FolderSelector - GUI and logic for folder selection

class FolderSelector:
    def __init__(self, config_file="config.json"):
      self.config_file = config_file
      self.input_folders = []
      self.output_folder = ""

    def select_input_folders(self, parent=None):
      folders = QFileDialog.getExistingDirectory(parent, "Select Input Folders")
      if folders:
        for folder in folders.split(";"):
          if any(file.lower().endswith((".png", ".jpg", ".jpeg")) for file in os.listdir(folder)):
             self.input_folders.append(folder)
          #self.save_to_config()
      return folders
    
    def select_output_folder(self, parent=None):
      folder = QFileDialog.getExistingDirectory(parent, "Select Output Folder")
      if folder:
        self.output_folder = folder
        #self.save_to_config()


    #TODO: Not enough time to implement, pass it to you guys, dunno if it is going to be relevant as well
    def save_to_config(self):
      config_data = {
        "input_folders": self.input_folders,
        "output_folder": self.output_folder,
      }
      with open(self.config_file, "w") as config_file:
        json.dump(config_data, config_file, indent=4)

    def load_from_config(self):
      if os.path.exists(self.config_file):
        with open(self.config_file, "r") as config_file:
          config_data = json.load(config_file)
          self.input_folders = config_data.get("input_folders", [])
          self.output_folder = config_data.get("output_folder", "")
