import pytest
import time
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication
import importlib
mecheye_available = importlib.util.find_spec("mecheye") is not None

pytestmark = pytest.mark.skipif(
    not mecheye_available,
    reason="Mech-Eye SDK not installed; skipping SDK-dependent tests."
)

@pytest.fixture(scope="session")
def app():
  return QApplication([])

@patch("utils.select_camera.MechmindConnection")
@patch("utils.select_camera.PhotoneoToolControl")
def test_initialization_performance(mock_photoneo, mock_mechmind, app):
  from utils.select_camera import CameraSelector
  mock_mechmind.return_value.find_cameras.return_value = []
  mock_photoneo.return_value.list_cameras.return_value = []

  start = time.time()
  selector = CameraSelector()
  duration = time.time() - start

  assert duration < 20  
