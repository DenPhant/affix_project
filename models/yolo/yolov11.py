from ultralytics import YOLO
from PIL import Image
from dotenv import load_dotenv
import time
import os
import matplotlib.pyplot as plt
import cv2
import torch
import torchvision

class YOLOv11:
  
  @staticmethod
  def yolo_detect(original_path, output_path):
    load_dotenv()
    start_time = time.time()
    model = YOLO(os.getenv("YOLO_MODEL_PATH"))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    image = cv2.imread(original_path)
    #Get image dimensions
    image_height, image_width = image.shape[:2]
      
    roi_width, roi_height = 750, 550
      
    #Calculate center of the image
    center_x, center_y = image_width // 2, image_height // 2
      
    #Calculate ROI coordinates
    roi_x = center_x - roi_width // 2
    roi_y = center_y - roi_height // 2
      
    cv2.rectangle(image, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (0, 255, 0), 2)
    roi = image[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
    try:
      results = model.predict(roi, conf=0.35)
      for result in results:
        try:
          #Other available attributes: boxes, masks, keypoints, probs, obb
          boxes = result.boxes  # Boxes object for bounding box outputs
          masks = result.masks  # Masks object for segmentation masks outputs
          keypoints = result.keypoints  # Keypoints object for pose outputs
          probs = result.probs  # Probs object for classification outputs
          obb = result.obb  # Oriented boxes object for OBB outputs

          result.save(output_path)  
          end_time = time.time()
          processing_time = end_time - start_time
          return processing_time
        except Exception as e:
          print(f"Error processing image {original_path}: {e}")
          break
    except Exception as e:
      #The issue might be because of CUDA version mismatch
      print(f"PyTorch version: {torch.__version__}")
      print(f"torchvision version: {torchvision.__version__}")
      print("CUDA Available:", torch.cuda.is_available())
      print("CUDA Device Count:", torch.cuda.device_count())
      print("CUDA Device Name:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "None")
      print(e)
      

    

