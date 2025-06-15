import pytest
from unittest.mock import MagicMock
from utils.picture_processor import Processor

@pytest.fixture
def dummy_parent():
    parent = MagicMock()
    parent.model = "Segment by lightening"
    return parent

def test_process_image_segment_by_lightening(dummy_parent, monkeypatch):
    processor = Processor(dummy_parent)
    input_path = "tests/resources/sample_input.png"
    output_path = "tests/resources/output.png"

    # Mock ImageProcessor
    from utils.image_processor import ImageProcessor
    monkeypatch.setattr(ImageProcessor, "segment_by_lightening", lambda inp, out: 0.123)

    result = processor.process_image(input_path, output_path)
    assert result == 0.123

