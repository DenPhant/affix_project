import time
import pytest
from unittest.mock import MagicMock
from utils.picture_processor import Processor

@pytest.fixture
def dummy_parent():
  parent = MagicMock()
  parent.model = "Segment by lightening"
  return parent

def test_process_image_performance(dummy_parent, monkeypatch):
  processor = Processor(dummy_parent)
  input_path = "tests/resources/test_image.png"
  output_path = "tests/resources/output.png"

  monkeypatch.setattr("utils.image_processor.ImageProcessor.segment_by_lightening", lambda inp, out: time.sleep(0.1))

  start = time.time()
  processor.process_image(input_path, output_path)
  duration = time.time() - start

  assert duration < 1  
