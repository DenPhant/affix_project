import pytest
from unittest.mock import patch, MagicMock
from PyQt5.QtWidgets import QApplication

import importlib
mecheye_available = importlib.util.find_spec("mecheye") is not None

pytestmark = pytest.mark.skipif(
    not mecheye_available,
    reason="Mech-Eye SDK not installed; skipping SDK-dependent tests."
)

# We need QApplication for any PyQt5 testing
@pytest.fixture(scope="session")
def app():
  return QApplication([])

@pytest.fixture
def mocked_cameras():
  mechmind_cameras = [MagicMock(model="MechModel1", serial_number="123", ip_address="192.168.0.2")]
  photoneo_cameras = ["PhoModel1 - SN456 - 192.168.0.3 - Photoneo"]
  return mechmind_cameras, photoneo_cameras

@patch("utils.select_camera.MechmindConnection")
@patch("utils.select_camera.PhotoneoToolControl")
def test_camera_selector_initialization(mock_photoneo, mock_mechmind, mocked_cameras, app):
  from utils.select_camera import CameraSelector
  mechmind_cameras, photoneo_cameras = mocked_cameras

  mock_mechmind.return_value.find_cameras.return_value = mechmind_cameras
  mock_photoneo.return_value.list_cameras.return_value = photoneo_cameras

  selector = CameraSelector()
  assert len(selector.cameras) == 2
  assert any("MechModel1" in cam for cam in selector.cameras)
  assert any("PhoModel1" in cam for cam in selector.cameras)
