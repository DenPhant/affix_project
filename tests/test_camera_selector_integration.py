import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
from utils.select_camera import CameraSelector

@pytest.fixture(scope="session")
def app():
  return QApplication([])

@patch("utils.select_camera.MechmindConnection")
@patch("utils.select_camera.PhotoneoToolControl")
def test_user_select_camera(mock_photoneo, mock_mechmind, app):
  mechmind_mock = MagicMock()
  mechmind_mock.model = "MM100"
  mechmind_mock.serial_number = "001"
  mechmind_mock.ip_address = "10.0.0.1"
  mock_mechmind.return_value.find_cameras.return_value = [mechmind_mock]
  mock_photoneo.return_value.list_cameras.return_value = []

  selector = CameraSelector()

  # Simulate user clicking first item
  selector.list_widget.setCurrentRow(0)
  selector.on_confirm()

  assert selector.get_selected_camera() is not None
  assert selector.get_model() == "MM100"
