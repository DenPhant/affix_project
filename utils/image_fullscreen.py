from PyQt5.QtWidgets import QDialog, QLabel, QHBoxLayout, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap


#Fullscreen picture view

class FullScreenViewer(QDialog):
  def __init__(self, parent, original_path=None, overlay_path=None):
    super().__init__(parent)
    self.setWindowTitle("Full Screen View")
    self.setWindowState(Qt.WindowFullScreen)
    self.setStyleSheet("background-color: black;")

    #Main layout
    main_layout = QVBoxLayout()
    main_layout.setContentsMargins(0, 0, 0, 0) 

    #Top bar layout
    top_bar_layout = QHBoxLayout()
    top_bar_layout.setContentsMargins(0, 0, 0, 0)

    close_btn = QPushButton("X")
    close_btn.setStyleSheet("""
      QPushButton {
        background-color: #f44336; 
        color: white; 
        font-weight: bold; 
        border: none; 
        border-radius: 10px; 
        padding: 5px 10px; 
        font-size: 14px;
      }
      QPushButton:hover {
        background-color: #d32f2f;
      }
      QPushButton:pressed {
        background-color: #b71c1c;
      }
    """)
    close_btn.setFixedSize(30, 30)
    close_btn.clicked.connect(self.close)

    #Add the close button to the top bar, push it to the right
    top_bar_layout.addStretch()
    top_bar_layout.addWidget(close_btn)

    #Image layout
    image_layout = QHBoxLayout()

    #Add the images to the dialog
    full_pic1 = QLabel()
    full_pic1.setAlignment(Qt.AlignCenter)
    full_pic2 = QLabel()
    full_pic2.setAlignment(Qt.AlignCenter)

    if original_path:
      pixmap1 = QPixmap(original_path)
      full_pic1.setPixmap(pixmap1.scaled(full_pic1.size(), Qt.KeepAspectRatio))
    else:
      full_pic1.setText("No Image Available")
      full_pic1.setStyleSheet("color: white; font-size: 18px;")

    if overlay_path:
      pixmap2 = QPixmap(overlay_path)
      full_pic2.setPixmap(pixmap2.scaled(full_pic2.size(), Qt.KeepAspectRatio))
    else:
      full_pic2.setText("No Image Available")
      full_pic2.setStyleSheet("color: white; font-size: 18px;")

    image_layout.addWidget(full_pic1)
    image_layout.addWidget(full_pic2)

    #Combine layouts
    main_layout.addLayout(top_bar_layout)  
    main_layout.addLayout(image_layout)  

    self.setLayout(main_layout)
