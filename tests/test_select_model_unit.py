import pytest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication
from utils.select_model import ModelSelectionDialog
import os

@pytest.fixture(scope="session")
def app():
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    return QApplication([])

def test_initial_population(app):
    models = [{"name": "M1", "description": "Desc1"}, {"name": "M2", "description": "Desc2"}]
    dialog = ModelSelectionDialog(models)
    assert dialog.model_list.count() == 2
    assert dialog.model_list.item(0).text() == "M1"

def test_show_description(app):
    models = [{"name": "M1", "description": "Desc1"}]
    dialog = ModelSelectionDialog(models)
    dialog.show_description(0)
    assert dialog.description_box.toPlainText() == "Desc1"
    dialog.show_description(-1)
    assert dialog.description_box.toPlainText() == ""


def test_accept_no_selection_warns(app):
    models = [{"name": "M1", "description": "Desc1"}]
    dialog = ModelSelectionDialog(models)
    dialog.model_list.setCurrentRow(-1)
    with patch("PyQt5.QtWidgets.QMessageBox.warning") as mocked_warning:
        dialog.accept()
        mocked_warning.assert_called_once()
        assert dialog.selected_model is None
