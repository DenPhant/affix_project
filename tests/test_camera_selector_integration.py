import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
import os
import importlib
mecheye_available = importlib.util.find_spec("mecheye") is not None

pytestmark = pytest.mark.skipif(
    not mecheye_available,
    reason="Mech-Eye SDK not installed; skipping SDK-dependent tests."
)


@pytest.fixture(scope="session")
def app():
  os.environ["QT_QPA_PLATFORM"] = "offscreen"
  return QApplication([])

@patch("utils.select_camera.MechmindConnection")
@patch("utils.select_camera.PhotoneoToolControl")
def test_user_select_camera(mock_photoneo, mock_mechmind, app):
  from utils.select_camera import CameraSelector
  mechmind_mock = MagicMock()
  mechmind_mock.model = "MM100"
  mechmind_mock.serial_number = "001"
  mechmind_mock.ip_address = "10.0.0.1"
  mock_mechmind.return_value.find_cameras.return_value = [mechmind_mock]
  mock_photoneo.return_value.list_cameras.return_value = []

  selector = CameraSelector()

  selector.list_widget.setCurrentRow(0)
  selector.on_confirm()

  assert selector.get_selected_camera() is not None
  assert selector.get_model() == "MM100"
