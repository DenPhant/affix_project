import pytest
import tempfile
import shutil
import numpy as np
import cv2
import os
from utils.image_processor import ImageProcessor

@pytest.fixture
def dummy_image(tmp_path):
  img = np.zeros((1200, 1600, 3), dtype=np.uint8)
  input_path = tmp_path / "input.png"
  output_path = tmp_path / "output.png"
  cv2.imwrite(str(input_path), img)
  return str(input_path), str(output_path)

@pytest.mark.parametrize("method", [
  ImageProcessor.convert_to_grayscale,
  ImageProcessor.convert_to_negative,
  ImageProcessor.segment_by_lightening,
  ImageProcessor.segment_by_darkening,
  ImageProcessor.wooden_pallet,
  ImageProcessor.segment_bin,
  ImageProcessor.just_take_the_image
])
def test_methods_no_exception(method, dummy_image):
  input_path, output_path = dummy_image
  processing_time = method(input_path, output_path)
  assert processing_time is not None
  assert os.path.exists(output_path)
