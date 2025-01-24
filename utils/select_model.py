from PyQt5.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
)
from PyQt5.QtCore import Qt

#Dialogue to select models, model name and description must be taken from config.json

class ModelSelectionDialog(QDialog):
    def __init__(self, models, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Model")
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
        self.setFixedSize(600, 400)
        self.selected_model = None

        #Main layout
        main_layout = QVBoxLayout(self)

        #Horizontal layout
        selection_layout = QHBoxLayout()

        #Model list
        self.model_list = QListWidget()
        self.model_list.setMinimumWidth(180)

        #Model description
        self.description_box = QTextEdit()
        self.description_box.setReadOnly(True)
        self.description_box.setMinimumWidth(350)

        #Add the widgets to the horizontal layout
        selection_layout.addWidget(self.model_list)
        selection_layout.addWidget(self.description_box)

        #Populate the model list
        self.models = models
        for model in models:
            self.model_list.addItem(model['name'])

        #Connect the list
        self.model_list.currentRowChanged.connect(self.show_description)

        #Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")  # Styled separately

        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)

        #Add widgets to the main layout
        main_layout.addWidget(QLabel("Available Models:"))
        main_layout.addLayout(selection_layout)  # Add the horizontal layout
        main_layout.addLayout(button_layout)

    def show_description(self, index):
        if index >= 0:
            self.description_box.setText(self.models[index]['description'])
        else:
            self.description_box.clear()

    def accept(self):
        current_row = self.model_list.currentRow()
        if current_row >= 0:
            self.selected_model = self.models[current_row]['name']
            super().accept()
        else:
            QMessageBox.warning(self, "No Selection", "Please select a model.")

    def get_selected_model(self):
        return self.selected_model
