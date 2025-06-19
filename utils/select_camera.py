from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QListWidgetItem
)
from PyQt5.QtCore import Qt

from utils.mechmind.mechmind_connection import MechmindConnection
from utils.photoneo.photoneo_tools import PhotoneoToolControl

class CameraSelector(QDialog):
  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle("Select Camera")
    self.setStyleSheet(
        """
        QDialog {
            background-color: #F7F7F7;
        }
        QListWidget {
            border: 1px solid #A6A6A6;
            background-color: #FFFFFF;
            padding: 5px;
        }
        QTextEdit {
            border: 1px solid #A6A6A6;
            background-color: #FAFAFA;
            padding: 5px;
        }
        QLabel {
            color: #333333;
        }
        QPushButton {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            min-width: 80px;
        }
        QPushButton:hover {
            background-color: #45A049;
        }
        QPushButton:pressed {
            background-color: #388E3C;
        }
        QPushButton#cancelButton {
            background-color: #F44336;
        }
        QPushButton#cancelButton:hover {
            background-color: #D32F2F;
        }
        QPushButton#cancelButton:pressed {
            background-color: #C62828;
        }
        """
    )

    self.cameras = []
    self.mechmind_connection = MechmindConnection()
    mechmind_cameras = self.mechmind_connection.find_cameras()
    if(any(mechmind_cameras)):
      for cam in mechmind_cameras:
        item = f"{cam.model} - {cam.serial_number} - {cam.ip_address} - MechMind"
        self.cameras.append(item)
    self.photoneo_connection = PhotoneoToolControl()
    photoneo_cameras = self.photoneo_connection.list_cameras()
    if(any(photoneo_cameras)):
      for cam in photoneo_cameras:
        self.cameras.append(cam)
    self.selected_camera = None

    self.init_ui()

  def init_ui(self):
    layout = QVBoxLayout(self)

    # Label for the list
    label = QLabel("Available Cameras:")
    layout.addWidget(label)

    # List widget to display cameras
    self.list_widget = QListWidget(self)
    for camera in self.cameras:
        item = QListWidgetItem(camera)
        item.setData(Qt.UserRole, camera)  # Store the camera data in the item
        self.list_widget.addItem(item)
    layout.addWidget(self.list_widget)

    # Confirm button
    confirm_button = QPushButton("Select", self)
    confirm_button.clicked.connect(self.on_confirm)
    layout.addWidget(confirm_button)

    # Cancel button
    cancel_button = QPushButton("Cancel", self)
    cancel_button.setObjectName("cancelButton")
    cancel_button.clicked.connect(self.reject)
    layout.addWidget(cancel_button)

  def on_confirm(self):
    selected_item = self.list_widget.currentItem()
    if selected_item:
      self.selected_camera = selected_item.data(Qt.UserRole)  # Retrieve the camera data
      self.accept()
    else:
      self.reject()

  def get_selected_camera(self):
    return self.selected_camera
  
  def get_model(self):
    return self.selected_camera.split(" - ")[0]