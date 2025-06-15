import sys
import json
from PyQt5.QtWidgets import (
  QApplication, QWidget, QVBoxLayout, QComboBox, QSpinBox, QDoubleSpinBox,
  QCheckBox, QPushButton, QLabel, QScrollArea, QFileDialog, QFormLayout
)
from utils.photoneo.photoneo_control import PhotoneoControl
from PyQt5.QtCore import Qt
from utils.photoneo.photoneo_tools import PhotoneoToolControl

class ConfigEditor(QWidget):
  def __init__(self, schema_file, device_id=None):
    super().__init__()
    self.setWindowTitle("MotionCam Configuration Editor")
    self.resize(600, 800)
    self.device_id = device_id
    if device_id is None:
      self.device_id = ""
    
    #schema_file = "./utils/photoneo/configs/cfg_schema_motioncam.json"
    with open(schema_file, 'r') as f:
      self.schema = json.load(f)

    connection = PhotoneoControl(self.device_id, "", 2)
    self.ia, self.features = connection.create_settings_ground()

    
    self.config = {}
    self.widgets = {}
    self.layout = QVBoxLayout()
    self.setLayout(self.layout)

    self.form_widget = QWidget()
    self.form_layout = QFormLayout()
    self.form_widget.setLayout(self.form_layout)

    scroll = QScrollArea()
    scroll.setWidgetResizable(True)
    scroll.setWidget(self.form_widget)
    self.layout.addWidget(scroll)

    self.load_config_widgets()

    self.load_btn = QPushButton("Import Config")
    self.load_btn.clicked.connect(self.load_config)
    self.layout.addWidget(self.load_btn)

    self.save_btn = QPushButton("Export Config")
    self.save_btn.clicked.connect(self.save_config)
    self.layout.addWidget(self.save_btn)

    self.apply_btn = QPushButton("Set")
    self.apply_btn.clicked.connect(self.print_config)
    self.layout.addWidget(self.apply_btn)

    self.close_btn = QPushButton("Close")
    self.close_btn.clicked.connect(self.close)
    self.layout.addWidget(self.close_btn)

  def load_config_widgets(self):
    for section, items in self.schema.items():
      self.form_layout.addRow(QLabel(f"=== {section} ==="))
      for key, props in items.items():
        tool = PhotoneoToolControl()
        val = tool.get_value(key, self.features)
        if val is not None:
          widget = self.create_widget(key, props, val)
          if widget:
            self.widgets[f"{section}.{key}"] = widget
            self.form_layout.addRow(key, widget)
        val = None

  def create_widget(self, key, props, val):
    
    typ = props.get("type")
    if typ == "bool":
      cb = QCheckBox()
      if val is not None: cb.setChecked(val)
      return cb
    elif typ == "int":
      max_val = props.get("max", 2147483647)
      min_val = props.get("min", -2147483648)
      if val > max_val or val < min_val:
        val = min_val
      if abs(max_val) > 2_147_483_647 or abs(min_val) > 2_147_483_648:
        sb = QDoubleSpinBox()
        sb.setDecimals(0)
        sb.setRange(min_val, max_val)
        sb.setValue(val)
      else:
        sb = QSpinBox()
        sb.setRange(min_val, max_val)
        sb.setValue(val)
      return sb
    elif typ == "float":
      dsb = QDoubleSpinBox()
      dsb.setDecimals(4)
      dsb.setRange(props.get("min", -1e9), props.get("max", 1e9))
      dsb.setValue(val)
      return dsb
    elif typ == "enum":
      combo = QComboBox()
      options = props.get("options") or props.get("values", [])
      combo.addItems(options)
      combo.setCurrentText(val)
      return combo
    return None

  def load_config(self):
    file_path, _ = QFileDialog.getOpenFileName(self, "Import Config File", "", "JSON Files (*.json)")
    if file_path:
      with open(file_path, 'r') as f:
        self.config = json.load(f)
      self.update_widgets()

  def update_widgets(self):
    for section, items in self.config.items():
      for key, value in items.items():
        widget = self.widgets.get(f"{section}.{key}")
        if widget:
          if isinstance(widget, QCheckBox):
            widget.setChecked(value)
          elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
            widget.setValue(value)
          elif isinstance(widget, QComboBox):
            idx = widget.findText(str(value))
            if idx >= 0:
              widget.setCurrentIndex(idx)

  def get_current_config(self):
    cfg = {}
    for path, widget in self.widgets.items():
      section, key = path.split(".")
      if section not in cfg:
        cfg[section] = {}
      if isinstance(widget, QCheckBox):
        cfg[section][key] = widget.isChecked()
      elif isinstance(widget, QSpinBox) or isinstance(widget, QDoubleSpinBox):
        cfg[section][key] = widget.value()
      elif isinstance(widget, QComboBox):
        cfg[section][key] = widget.currentText()
    return cfg

  def save_config(self):
    cfg = self.get_current_config()
    file_path, _ = QFileDialog.getSaveFileName(self, "Export Config File", "", "JSON Files (*.json)")
    if file_path:
      with open(file_path, 'w') as f:
        json.dump(cfg, f, indent=2)

  def print_config(self):
    cfg = self.get_current_config()
    try:
      tool = PhotoneoToolControl()
      tool.apply_config_to_motioncam(config = cfg, features=self.features)

      print("✔ Configuration applied successfully.")
    except Exception as e:
      print("❌ Failed to apply configuration:", str(e))

#Entry point for main application
def open_photoneo_config(parent=None):
  device = None
  if parent:
    info = parent.camera_info.split(" - ")
    device = info[1]
  editor = ConfigEditor("./utils/photoneo/configs/cfg_schema_motioncam.json",device_id=device)
  if parent:
    editor.setParent(parent)
  editor.setWindowModality(Qt.NonModal)
  editor.setAttribute(Qt.WA_DeleteOnClose)
  editor.show()
  return editor