import os
import json
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from utils.select_folder import FolderSelector

@pytest.fixture
def temp_config_file(tmp_path):
    return tmp_path / "config.json"

def test_initial_state(temp_config_file):
    fs = FolderSelector(config_file=str(temp_config_file))
    assert fs.input_folders == []
    assert fs.output_folder == ""
    assert fs.config_file == str(temp_config_file)


@patch("utils.select_folder.QFileDialog.getExistingDirectory")
def test_select_input_folders_with_no_image_files(mock_dialog, tmp_path):
    folder = tmp_path / "folder"
    folder.mkdir()
    (folder / "doc.txt").write_text("dummy")

    mock_dialog.return_value = f"{folder}"

    fs = FolderSelector()
    selected = fs.select_input_folders(parent=None)

    assert selected == f"{folder}"
    assert fs.input_folders == []

@patch("utils.select_folder.QFileDialog.getExistingDirectory")
def test_select_output_folder(mock_dialog, tmp_path):
    folder = tmp_path / "output_folder"
    folder.mkdir()

    mock_dialog.return_value = str(folder)

    fs = FolderSelector()
    fs.select_output_folder(parent=None)
    assert fs.output_folder == str(folder)

def test_save_and_load_config(tmp_path):
    config_file = tmp_path / "config.json"
    fs = FolderSelector(config_file=str(config_file))

    fs.input_folders = ["input1", "input2"]
    fs.output_folder = "output_folder"

    fs.save_to_config()

    assert config_file.exists()

    fs2 = FolderSelector(config_file=str(config_file))
    fs2.load_from_config()

    assert fs2.input_folders == ["input1", "input2"]
    assert fs2.output_folder == "output_folder"

def test_load_from_config_file_missing(tmp_path):
    config_file = tmp_path / "missing_config.json"
    fs = FolderSelector(config_file=str(config_file))
    fs.load_from_config()
    assert fs.input_folders == []
    assert fs.output_folder == ""
