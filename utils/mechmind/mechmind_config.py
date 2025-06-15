# mechmind_config_editor.py

import sys
import json
import numpy as np
from PyQt5.QtWidgets import (
  QApplication, QWidget, QVBoxLayout, QComboBox, QSpinBox, QDoubleSpinBox,
  QCheckBox, QPushButton, QLabel, QScrollArea, QFileDialog, QFormLayout, QMessageBox
)
from PyQt5.QtCore import Qt

from mecheye.shared import *
from mecheye.area_scan_3d_camera import *
from mecheye.area_scan_3d_camera_utils import *



class MechmindConnection:
  def convert_parameter(self, type):
    if type == 0: return "INT"
    elif type == 1: return "FLOAT"
    elif type == 2: return "BOOL"
    elif type == 3: return "ENUM"
    elif type == 4: return "ROI"
    elif type == 5: return "RANGE"
    elif type == 6: return "FLOAT ARRAY"
    elif type == 7: return "ROI ARRAY"
    elif type == 8: return "PROFILE ROI"
    else: return "UNKNOWN"

  def find_and_connect(self, ip_address=None):
    camera = Camera()
    info_list = camera.discover_cameras()
    if len(info_list) == 0:
      print("No cameras found")
      return None
    if ip_address:
      for info in info_list:
        if info.ip_address == ip_address:
          camera.connect(ip_address)
          print("Connected to", info.model)
          return camera
      print("Camera with given IP not found")
      return None
    else:
      camera_info = info_list[0]
      camera.connect(camera_info.ip_address)
      print("Connected to", camera_info.model)
      return camera


class MechmindConfigEditor(QWidget):
  def __init__(self, camera_ip=None, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Mechmind Configuration Editor")
    self.resize(600, 800)
    self.connection = MechmindConnection()
    self.camera = self.connection.find_and_connect(camera_ip)
    if self.camera is None:
      QMessageBox.critical(self, "Error", "Failed to connect to Mechmind camera")
      self.close()
      return

    self.layout = QVBoxLayout()
    self.setLayout(self.layout)

    self.form_widget = QWidget()
    self.form_layout = QFormLayout()
    self.form_widget.setLayout(self.form_layout)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(self.form_widget)
    self.layout.addWidget(scroll)

    self.widgets = {}
    self.load_camera_parameters()

    self.apply_btn = QPushButton("Apply Settings")
    self.apply_btn.clicked.connect(self.apply_settings)
    self.layout.addWidget(self.apply_btn)

  def load_camera_parameters(self):
    user_manager = self.camera.user_set_manager()
    error, user_sets = user_manager.get_all_user_set_names()
    if error.error_code != 0:
      QMessageBox.critical(self, "Error", "Failed to read user sets")
      return

    user_manager.select_user_set(user_sets[0])
    current_set = self.camera.current_user_set()

    self.parameters = current_set.get_available_parameters()
    self.current_set = current_set

    for param in self.parameters:
      name = param.name()
      type_ = param.type()
      type_name = self.connection.convert_parameter(type_)
      description = param.description()
      writable = param.is_writable()
      readable = param.is_readable()

      print(name)
      print("Type -", type_, ",", type_name)
      print(description)
      print("Writable -", writable)
      print("Readable -", readable)
      print("___________________________________")

      if not readable:
        print(f"Skipping unreadable parameter: {name}")
        continue

      try:
        widget = None

        if type_name == "INT":
          err, val = current_set.get_int_value(name)
          if err.error_code != 0:
            print(f"Failed to get INT value for {name}: {err}")
            continue

          # Try to get range safely
          try:
            err, param_range = current_set.get_parameter_range(name)
            if err.error_code == 0:
              min_val = int(param_range.min())
              max_val = int(param_range.max())
            else:
              print(f"Range not available for INT parameter {name}, using defaults")
              min_val, max_val = 0, 2147483647
          except AttributeError:
            print(f"get_parameter_range not supported for INT parameter {name}, using defaults")
            min_val, max_val = 0, 2147483647

          widget = QSpinBox()
          widget.setRange(min_val, max_val)
          widget.setValue(val)

        elif type_name == "FLOAT":
          err, val = current_set.get_float_value(name)
          if err.error_code != 0:
            print(f"Failed to get FLOAT value for {name}: {err}")
            continue

          # Try to get range safely
          try:
            err, param_range = current_set.get_parameter_range(name)
            if err.error_code == 0:
              min_val = param_range.min()
              max_val = param_range.max()
            else:
              print(f"Range not available for FLOAT parameter {name}, using defaults")
              min_val, max_val = 0.0, 1000000.0
          except AttributeError:
            print(f"get_parameter_range not supported for FLOAT parameter {name}, using defaults")
            min_val, max_val = 0.0, 1000000.0

          widget = QDoubleSpinBox()
          widget.setDecimals(4)
          widget.setRange(min_val, max_val)
          widget.setValue(val)


        elif type_name == "BOOL":
          err, val = current_set.get_bool_value(name)
          if err.error_code != 0:
            print(f"Failed to get BOOL value for {name}: {err}")
            continue

          widget = QCheckBox()
          widget.setChecked(val)

        elif type_name == "ENUM":
          err, entries = current_set.get_enum_entries(name)
          if err.error_code != 0:
            print(f"Failed to get ENUM entries for {name}: {err}")
            continue

          err, val = current_set.get_enum_value(name)
          if err.error_code != 0:
            print(f"Failed to get ENUM value for {name}: {err}")
            continue

          widget = QComboBox()
          enum_dict = {}
          for entry in entries:
            enum_dict[entry.symbolic()] = entry.value()
            widget.addItem(entry.symbolic(), entry.value())
          widget.setCurrentIndex(widget.findData(val))
          widget.enum_dict = enum_dict

        else:
          print(f"Skipping unsupported parameter type: {name} ({type_name})")
          continue

        widget.setDisabled(not writable)
        self.form_layout.addRow(f"{name} ({type_name})", widget)
        self.widgets[name] = (param, widget, type_, writable)

      except Exception as e:
        print(f"Failed to process parameter {name}: {e}")



  def apply_settings(self):
    for name, (param, widget, type_, writable) in self.widgets.items():
      type_name = MechmindConnection.convert_parameter(self,type_)
      try:
        if type_name == "INT":
          val = widget.value()
          self.current_set.set_int_value(name, val)
        elif type_name == "FLOAT":
          val = widget.value()
          self.current_set.set_float_value(name, val)
        elif type_name == "BOOL":
          val = widget.isChecked()
          self.current_set.set_bool_value(name, val)
        elif type_name == "ENUM":
          val = widget.currentData()
          self.current_set.set_enum_value(name, val)
      except Exception as e:
        QMessageBox.warning(self, "Warning", f"Failed to set {name}: {e}")


    QMessageBox.information(self, "Success", "Settings applied successfully.")


# This is the callable entry point from other files
def open_mechmind_config(parent=None, camera_ip=None):
  editor = MechmindConfigEditor(camera_ip, parent=parent)
  if parent:
    editor.setParent(parent)
  editor.setWindowModality(Qt.NonModal)
  editor.setAttribute(Qt.WA_DeleteOnClose)
  editor.show()
  return editor
