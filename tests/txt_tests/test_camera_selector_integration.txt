import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from PyQt5.QtWidgets import QApplication
import os

# Check whether MechmindConnection can be imported safely
try:
    from utils.mechmind.mechmind_connection import MechmindConnection
    mecheye_available = True
except (ImportError, OSError):
    mecheye_available = False

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

    # Create a fake camera with required attributes
    mock_cam = MagicMock()
    mock_cam.model = "MM100"
    mock_cam.serial_number = "001"
    mock_cam.ip_address = "10.0.0.1"
    mock_mechmind.return_value.find_cameras.return_value = [mock_cam]
    mock_photoneo.return_value.list_cameras.return_value = []

    selector = CameraSelector()
    assert selector.list_widget.count() == 1
    assert "MM100" in selector.list_widget.item(0).text()

    selector.list_widget.setCurrentRow(0)
    selector.on_confirm()

    assert selector.get_selected_camera() is not None
    assert selector.get_model() == "MM100"
