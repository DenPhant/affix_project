import pytest
import os
from utils.image_processor import ImageProcessor

@pytest.fixture
def test_image_path():
  return "tests/resources/test_image.png"

@pytest.fixture
def output_path(tmp_path):
  return str(tmp_path / "output.png")

def test_segment_by_lightening_full(test_image_path, output_path):
  processing_time = ImageProcessor.segment_by_lightening(test_image_path, output_path)
  assert processing_time > 0
  assert os.path.exists(output_path)
  assert os.path.getsize(output_path) > 0

def test_segment_bin_full(test_image_path, output_path):
  processing_time = ImageProcessor.segment_bin(test_image_path, output_path)
  assert processing_time > 0
  assert os.path.exists(output_path)
