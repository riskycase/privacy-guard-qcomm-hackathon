import pytest
import numpy as np
from unittest.mock import Mock, patch
import cv2
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from face_counter.detector import FaceDetector

@pytest.fixture
def mock_session():
    """Create a mock ONNX session"""
    session = Mock()
    session.get_inputs.return_value = [Mock(name='input', shape=[1, 1, 480, 640])]
    session.get_outputs.return_value = [Mock(name='output')]
    return session

@pytest.fixture
def detector(mock_session):
    """Create a FaceDetector instance with mocked session"""
    with patch('onnxruntime.InferenceSession', return_value=mock_session):
        detector = FaceDetector("dummy_model.onnx")
        detector.session = mock_session
        detector.input_name = 'input'
        detector.output_names = ['output']
        return detector

def test_preprocess_image(detector):
    """Test image preprocessing"""
    # Create a test image (100x100 RGB)
    test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    
    # Process the image
    processed = detector.preprocess_image(test_image)
    
    # Check output shape and type
    assert processed.shape == (1, 1, 480, 640)  # Batch, Channel, Height, Width
    assert processed.dtype == np.uint16
    assert processed.max() <= 65535
    assert processed.min() >= 0

def test_find_peaks(detector):
    """Test peak finding in heatmap"""
    # Create a test heatmap with known peaks
    heatmap = np.zeros((10, 10))
    heatmap[3, 3] = 1.0  # Peak 1
    heatmap[7, 7] = 0.8  # Peak 2
    heatmap[5, 5] = 0.3  # Below threshold
    
    peaks = detector._find_peaks(heatmap, threshold=0.5)
    
    # Should find 2 peaks above threshold
    assert len(peaks) == 2
    assert (3, 3) in peaks
    assert (7, 7) in peaks
    assert (5, 5) not in peaks

def test_detect_faces(detector, mock_session):
    """Test face detection with mock model output"""
    # Create a test image
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Mock model output (heatmap with two peaks)
    mock_heatmap = np.zeros((1, 1, 60, 80))
    mock_heatmap[0, 0, 30, 40] = 1.0  # Peak 1
    mock_heatmap[0, 0, 45, 60] = 0.8  # Peak 2
    mock_session.run.return_value = [mock_heatmap]
    
    # Detect faces
    boxes = detector.detect_faces(test_image)
    
    # Should detect 2 faces
    assert len(boxes) == 2
    # Check box format (x, y, w, h)
    for box in boxes:
        assert len(box) == 4
        assert all(isinstance(x, int) for x in box)
        assert box[2] > 0 and box[3] > 0  # width and height should be positive

def test_count_faces(detector, mock_session):
    """Test face counting"""
    # Create a test image
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    
    # Mock model output with three peaks
    mock_heatmap = np.zeros((1, 1, 60, 80))
    mock_heatmap[0, 0, 30, 40] = 1.0  # Peak 1
    mock_heatmap[0, 0, 45, 60] = 0.8  # Peak 2
    mock_heatmap[0, 0, 15, 20] = 0.9  # Peak 3
    mock_session.run.return_value = [mock_heatmap]
    
    # Count faces
    count = detector.count_faces(test_image)
    
    # Should count 3 faces
    assert count == 3

def test_detect_faces_empty_frame(detector):
    """Test face detection with empty frame"""
    empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    boxes = detector.detect_faces(empty_frame)
    assert len(boxes) == 0

def test_detect_faces_invalid_input(detector):
    """Test face detection with invalid input"""
    # Test with None input
    result = detector.detect_faces(None)
    assert result == []  # Should return empty list for None input
    
    # Test with too small image
    small_image = np.zeros((10, 10))
    result = detector.detect_faces(small_image)
    assert result == []  # Should return empty list for invalid image 