import pytest
import time
from utils.image_processor import ImageProcessor

@pytest.fixture
def test_image_path():
  return "tests/resources/test_image.png"

@pytest.fixture
def output_path(tmp_path):
  return str(tmp_path / "output.png")

@pytest.mark.parametrize("method", [
  ImageProcessor.segment_by_lightening,
  ImageProcessor.segment_by_darkening,
  ImageProcessor.segment_bin
])
def test_performance(method, test_image_path, output_path):
  start = time.time()
  processing_time = method(test_image_path, output_path)
  end = time.time()
  assert processing_time <= (end - start)
  assert processing_time < 5  
