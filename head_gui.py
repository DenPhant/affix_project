from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QRadioButton, QLabel, QScrollArea, QGridLayout, QGroupBox, QFileDialog, QMessageBox, QButtonGroup, QDialog, QSpacerItem, QSizePolicy
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtGui import QPixmap
import json
import os
from utils.select_folder import FolderSelector
#from utils.image_processor import ImageProcessor
from utils.image_fullscreen import FullScreenViewer
from utils.select_model import ModelSelectionDialog
from utils.select_camera import CameraSelector
#from utils.mechmind_connection import MechmindConnection
from utils.configuration_manager import ConfigurationManager
from utils.picture_processor import Processor
#from utils.photoneo.photoneo_control import PhotoneoControl
from utils.photoneo.photoneo_config_editor import open_photoneo_config

#General UI, with more than 600 lines of code,
#A lot of code went to just add widgets to layouts, styling them and saparation by empty lines
#It can be confusing, especially with picture updating, 
#but I tried to keep it as clean, simple and easy understandable as possible

class GeneralWindow(QMainWindow):
  config_path = "config.json"

  def __init__(self):
    super().__init__()
    self.setWindowTitle("GUI")
    self.setGeometry(300, 100, 1200, 900)
    self.setStyleSheet("background-color: #E2DDD9; font-family: Arial, sans-serif; font-size: 14px;")
    self.input_pics = []
    self.output_pics = []
    self.max_index = 0
    self.processor = Processor(self)

    #Work mode - get images from folder (0) or from camera (1) default - 0
    self.work_mode = 0

    #Main Layout
    main_layout = QGridLayout()

    #Initialize variables for pictures
    self.input_folders = []
    self.pictures = []
    self.current_index = -1
    self.output_folder = ""
    self.output_folder_file_count = 0
    self.model = ""
    self.connection = None
    self.camera_info = ""
    self.camera = None
    self.processing_times = []

    #Pic Boxes
    self.pic1 = QLabel("Picture Box 1")
    self.pic1.setFixedSize(300, 300)
    self.pic1.setStyleSheet("""
      QLabel {
        background-color: #fcac94;
        border: 2px solid #1b8a99;
        border-radius: 10px;
        color: #333333;
      }
    """)
    self.pic1.setAlignment(Qt.AlignCenter)
    self.pic1.mousePressEvent = self.handle_picture_click

    self.pic2 = QLabel("Picture Box 2")
    self.pic2.setFixedSize(300, 300)
    self.pic2.setStyleSheet("""
      QLabel {
        background-color: #fcac94;
        border: 2px solid #1b8a99;
        border-radius: 10px;
        color: #333333;
      }
    """)
    self.pic2.setAlignment(Qt.AlignCenter)
    self.pic2.mousePressEvent = self.handle_picture_click

    #Prev/Next Buttons
    self.prev_btn = QPushButton("←")
    self.prev_btn.setFixedSize(100, 50)
    self.prev_btn.setStyleSheet("""
      QPushButton {
        background-color: #f45f30;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 24px;
        
      }
      QPushButton:hover {
        background-color: #d94e2b;
      }
    """)
    self.prev_btn.clicked.connect(self.show_prev_picture)

    self.next_btn = QPushButton("→")
    self.next_btn.setFixedSize(100, 50)
    self.next_btn.setStyleSheet("""
      QPushButton {
        background-color: #f45f30;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 24px;
        
      }
      QPushButton:hover {
        background-color: #d94e2b;
      }
    """)
    self.next_btn.clicked.connect(self.show_next_picture)

    self.picture_time = QLabel("0")
    self.picture_time.setAlignment(Qt.AlignCenter)
    self.picture_time.setStyleSheet("color: #555555;")

    self.picture_status = QLabel("0 / 0")
    self.picture_status.setAlignment(Qt.AlignCenter)
    self.picture_status.setStyleSheet(" color: #555555;")

    #Status Layout centered, " " is a spacer, as long as it works
    status_layout = QVBoxLayout()
    status_layout.addWidget(QLabel(" "))
    status_layout.addWidget(QLabel(" "))
    status_layout.addWidget(QLabel(" "))
    status_layout.addWidget(self.picture_status)
    status_layout.addWidget(self.picture_time)
    status_layout.addWidget(QLabel(" "))
    status_layout.addWidget(QLabel(" "))
    status_layout.addWidget(QLabel(" "))

    #Picture Layout
    pic_layout = QHBoxLayout()
    pic_layout.addWidget(self.prev_btn)
    pic_layout.addWidget(self.pic1)
    pic_layout.addLayout(status_layout)
    pic_layout.addWidget(self.pic2)
    pic_layout.addWidget(self.next_btn)

    main_layout.addLayout(pic_layout, 0, 0, 1, 4)

    #Language Settings and Logos NOT IMPLEMENTED
    lang_logo_layout = QVBoxLayout()

    self.lang_btn = QPushButton("Language Settings")
    self.lang_btn.setFixedSize(200, 50)
    self.lang_btn.setStyleSheet("""
      QPushButton {
        background-color: #1b8a99;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 16px;
      }
      QPushButton:hover {
        background-color: #166f7a;
      }
    """)
    self.lang_btn.clicked.connect(self.not_implemented)
    lang_logo_layout.addWidget(self.lang_btn)

    image_paths = ["assets/affix_logo-no-bg.png", "assets/fontys_logo-no-bg.png", "assets/NXTGEN_logo.jpg"]

    for i, image_path in enumerate(image_paths):
      logo = QLabel()
      logo.setFixedSize(200, 100)
      logo.setAlignment(Qt.AlignCenter)
  
      pixmap = QPixmap(image_path)

      if pixmap.isNull():
        logo.setText(f"Image {i + 1} not found")
        logo.setStyleSheet("color: red; font-style: italic;")
      else:
        logo.setPixmap(pixmap.scaled(logo.size(), aspectRatioMode=1))

      
      lang_logo_layout.addWidget(logo)

    main_layout.addLayout(lang_logo_layout, 0, 4)

    #Buttons for Actions
    button_layout = QVBoxLayout()
    
    font = QFont()
    font.setPointSize(50)

    self.start_btn = QPushButton("▶")
    self.start_btn.clicked.connect(self.start_processing)
    self.start_btn.setFont(font)
    self.start_btn.setStyleSheet("""
      QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 30px;
      }
      QPushButton:hover {
        background-color: #3e8e41;
      }
    """)

    #Stop Button - NOT IMPLEMENTED
    self.stop_btn = QPushButton("STOP")
    font.setPointSize(14)
    self.stop_btn.setFont(font)
    self.stop_btn.setStyleSheet("""
      QPushButton {
        background-color: #ff4d4d;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #e63939;
      }
    """)
    self.stop_btn.clicked.connect(self.not_implemented)

    #Save Configuration Button - NOT IMPLEMENTED
    self.save_cfg_btn = QPushButton("Save Configuration")
    self.save_cfg_btn.setStyleSheet("""
      QPushButton {
        background-color: #1b8a99;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #166f7a;
      }
    """)
    self.save_cfg_btn.clicked.connect(self.not_implemented)

    #Load Configuration Button - NOT IMPLEMENTED
    self.load_cfg_btn = QPushButton("Load Configuration")
    self.load_cfg_btn.setStyleSheet("""
      QPushButton {
        background-color: #1b8a99;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #166f7a;
      }
    """)
    self.load_cfg_btn.clicked.connect(self.load_configuration)
    self.config_managers = []

    #Edit Configuration Button - NOT IMPLEMENTED
    self.edit_cfg_btn = QPushButton("Edit Configuration")
    self.edit_cfg_btn.setStyleSheet("""
      QPushButton {
        background-color: #1b8a99;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #166f7a;
      }
    """)
    self.edit_cfg_btn.clicked.connect(self.not_implemented)
    
    

    #Add the buttons to the layout and keep them "fancyyy"
    for btn in [self.start_btn, self.stop_btn,  self.load_cfg_btn]:
      btn.setFixedSize(200, 50)
      button_layout.addWidget(btn)

    main_layout.addLayout(button_layout, 1, 0, 2, 1)

    #Scroll Area for Input Folders, never selected a lot, dunno if works
    scroll_layout = QVBoxLayout()

    self.input_folder_btn = QPushButton("Add Input Folder")
    self.input_folder_btn.clicked.connect(self.add_input_folder)
    self.input_folder_btn.setStyleSheet("""
      QPushButton {
        background-color: #f45f30;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #d94e2b;
      }
    """)

    #Output Folder Selection
    self.output_folder_btn = QPushButton("Select Output Folder")
    self.output_folder_btn.clicked.connect(self.set_output_folder)
    self.output_folder_btn.setStyleSheet("""
      QPushButton {
        background-color: #f45f30;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #d94e2b;
      }
    """)

    self.output_folder_label = QLabel("")
    self.output_folder_label.setStyleSheet("color: #333333;")


    self.model_label = QLabel("Model: Not selected")
    self.model_label.setFont(font)
    self.model_label.setStyleSheet("color: #333333;")
    
    

    #Model Selection Button
    self.change_model_btn = QPushButton("Select Model")
    self.change_model_btn.clicked.connect(self.open_model_dialog)
    self.change_model_btn.setStyleSheet("""
      QPushButton {
        background-color: #1b8a99;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #166f7a;
      }
    """)

    self.camera_label = QLabel("Camera: Not selected")
    self.camera_label.setFont(font)
    self.camera_label.setStyleSheet("color: #333333;")
  
    self.camera_btn = QPushButton("Select Camera")
    self.camera_btn.clicked.connect(self.open_camera_dialog)
    self.camera_btn.setStyleSheet(
      """
      QPushButton {
        background-color: #1b8a99;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #166f7a;
      }
    """)

    #Add the widgets to the layout and keep them "fancyyy"
    for widget in [self.input_folder_btn, self.output_folder_btn, self.output_folder_label, self.model_label, self.change_model_btn, self.camera_label, self.camera_btn]:
      scroll_layout.addWidget(widget)

    self.scroll_area = QScrollArea()
    self.scroll_area_content = QWidget()
    self.scroll_area_layout = QVBoxLayout()
    self.scroll_area_content.setLayout(self.scroll_area_layout)
    self.scroll_area.setWidget(self.scroll_area_content)
    self.scroll_area.setWidgetResizable(True)
    self.scroll_area.setStyleSheet("""
      QScrollArea {
        border: 2px solid #1b8a99;
        background-color: #E2DDD9;
      }
    """)
    scroll_layout.addWidget(self.scroll_area)

    main_layout.addLayout(scroll_layout, 1, 1, 2, 2)

    #Radio Buttons for Object and Surface Types
    radio_layout_objects = QGridLayout()
    radio_layout_surface = QGridLayout()

    surface_group = QButtonGroup()
    surface_group.setExclusive(True)

    object_group = QButtonGroup()
    object_group.setExclusive(True)

    #Load Configuration for Radio Buttons
    if os.path.exists(self.config_path):
      with open(self.config_path, "r") as f:
        config_data = json.load(f)
        object_types = config_data.get("object_types", [])
        surface_types = config_data.get("surface_types", [])

    #Create sexy buttons
    for i in range(len(object_types)):
      object_radio = QRadioButton(object_types[i])
      object_group.addButton(object_radio)
      object_radio.setStyleSheet("""
        QRadioButton {
          border: none;
          font-size: 14px;
          color: #333333;
        }
        QRadioButton::indicator {
          width: 14px;
          height: 14px;
          border: 1px solid #ccc;
          border-radius: 7px;
          background-color: white;
        }
        QRadioButton::indicator:checked {
          background-color: #1b8a99;
          border-color: #007bff;
        }
      """)
      radio_layout_objects.addWidget(object_radio, i + 1, 1)
      if i == 0:
        object_radio.setChecked(True)

    for i in range(len(surface_types)):
      surface_radio = QRadioButton(surface_types[i])
      surface_group.addButton(surface_radio)
      surface_radio.setStyleSheet("""
        QRadioButton {
          border: none;
          font-size: 14px;
          color: #333333;
        }
        QRadioButton::indicator {
          width: 14px;
          height: 14px;
          border: 1px solid #ccc;
          border-radius: 7px;
          background-color: white;
        }
        QRadioButton::indicator:checked {
          background-color: #1b8a99;
          border-color: #007bff;
        }
      """)
      radio_layout_surface.addWidget(surface_radio, i + 1, 0)
      if i == 0:
        surface_radio.setChecked(True)

    #Object Type Options GroupBox
    radio_group_box_objects = QGroupBox("Object Type Options")
    radio_group_box_objects.setStyleSheet("""
      QGroupBox {
        color: #333333;
        border: 2px solid #1b8a99;
        border-radius: 8px;
        margin-top: 10px;
        padding: 10px;
      }
    """)
    radio_group_box_objects.setLayout(radio_layout_objects)
    main_layout.addWidget(radio_group_box_objects, 1, 4, 2, 1)

    #Surface Type Options GroupBox
    radio_group_box_surface = QGroupBox("Surface Type Options")
    radio_group_box_surface.setStyleSheet("""
      QGroupBox {
        color: #333333;
        border: 2px solid #1b8a99;
        border-radius: 8px;
        margin-top: 10px;
        padding: 10px;
      }
    """)
    radio_group_box_surface.setLayout(radio_layout_surface)
    main_layout.addWidget(radio_group_box_surface, 1, 3, 2, 1)

    #Main Widget
    central_widget = QWidget()
    central_widget.setLayout(main_layout)
    self.setCentralWidget(central_widget)

  def open_camera_dialog(self):
    
    #if not cameras:
    #  QMessageBox.warning(self, "No Cameras", "No cameras found.")
    #  return

    dialog = CameraSelector(self) 
    selected_camera = None  
    if dialog.exec_() == QDialog.Accepted:
      selected_camera = dialog.get_selected_camera()
      QMessageBox.information(self, "Selected Camera", f"You selected: {selected_camera}")
      self.work_mode = 1
      self.camera_label.setText(f"Camera: {dialog.get_model()}")

    if selected_camera:
      self.camera_info = selected_camera
      #self.camera = self.connection.connect(self.camera_info)
    

  def open_model_dialog(self):
    try:
      with open("config.json", "r") as file:
        config = json.load(file)
        models = config.get("models", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
      QMessageBox.critical(self, "Error", f"Failed to load models: {e}")
      return

    if not models:
      QMessageBox.warning(self, "No Models", "No models found in the configuration.")
      return

    dialog = ModelSelectionDialog(models, self)
    if dialog.exec_() == QDialog.Accepted:
      selected_model = dialog.get_selected_model()
      self.model_label.setText(f"Model: {selected_model}")
      self.model = selected_model
      #QMessageBox.information(self, "Selected Model", f"You selected: {selected_model}")



  def add_input_folder(self):
    folder = FolderSelector.select_input_folders(self)
    if folder:
      self.update_scroll_area()
      self.load_pictures()

  


  def set_output_folder(self):
    folder = QFileDialog.getExistingDirectory(self, "Select Output Folder")
    if folder:
      self.output_folder = folder
      with os.scandir(self.output_folder) as entries:
          self.output_folder_file_count = sum(1 for entry in entries if entry.is_file())
      self.output_folder_label.setText("Output:" + folder)



  def update_scroll_area(self):
    #Clear the scroll area layout
    while self.scroll_area_layout.count() > 0:
      item = self.scroll_area_layout.takeAt(0)
      widget = item.widget()
      if widget:
        widget.deleteLater()

    #Add updated folder paths
    for folder in self.input_folders:
      folder_label = QLabel(folder)
      self.scroll_area_layout.addWidget(folder_label)



  def load_pictures(self):
    self.pictures.clear()
    for folder in self.input_folders:
      for file in os.listdir(folder):
        if file.lower().endswith((".png", ".jpg", ".jpeg")):
          self.pictures.append(os.path.join(folder, file))
    self.current_index = 0 if self.pictures else -1
    self.max_index = len(self.pictures) - 1 if self.pictures else 0
    self.update_picture_boxes()



  def update_picture_boxes(self):
    if self.current_index >= 0 and self.pictures:
      original_path = self.pictures[self.current_index]
      self.pic1.setPixmap(QPixmap(original_path).scaled(self.pic1.size(), aspectRatioMode=1))
      if(self.current_index < len(self.output_pics)):
        self.pic2.setPixmap(QPixmap(self.output_pics[self.current_index]).scaled(self.pic2.size(), aspectRatioMode=1))
      else:
        self.pic2.clear()
      self.picture_status.setText(f"{self.current_index + 1} / { len(self.pictures)}")
      if self.processing_times:
        self.picture_time.setText(f"{self.processing_times[self.current_index]:.2f} s")
    else:
      self.pic1.clear()
      self.pic2.clear()
      self.picture_status.setText("0 / 0")
  


  def start_processing(self):
    self.processor.start_processing()

  def show_prev_picture(self):
    if self.current_index > 0:
      self.current_index -= 1
      self.update_picture_boxes()
    elif self.current_index == 0:
      self.current_index = self.max_index
      self.update_picture_boxes()

  def show_next_picture(self):
    if self.current_index < len(self.pictures) - 1:
      self.current_index += 1
      self.update_picture_boxes()
    elif self.current_index == self.max_index:
      self.current_index = 0
      self.update_picture_boxes()

  def load_configuration(self):
    print (self.camera_info)
    manager = ConfigurationManager(self.camera_info)
    self.config_managers.append(manager)
    manager.load()
    # Optional: connect window close signal to cleanup
    if manager.config_window:
      manager.config_window.destroyed.connect(lambda: self.config_managers.remove(manager))

  def handle_picture_click(self, event):
    #Show the full-screen viewer
    viewer = FullScreenViewer(self, self.input_pics[self.current_index], self.output_pics[self.current_index])
    viewer.exec_()


  def not_implemented(self):
    QMessageBox.information(self, "Not Implemented", "This feature is not implemented yet.")