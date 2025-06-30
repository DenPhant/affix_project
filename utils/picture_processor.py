import os
import time
import cv2
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QPixmap

from models.yolo.yolov11 import YOLOv11
from utils.image_processor import ImageProcessor
from utils.camera_processor import CameraProcessor

from pathlib import Path
from dotenv import load_dotenv

class Processor:
  load_dotenv()
  def __init__(self, parent):
    self.parent = parent

  def show_warning(self, message):
    warning = QMessageBox()
    warning.setStyleSheet("background-color: white;")
    QMessageBox.warning(None, "Error", message)

  def start_processing(self):
    if self.parent.work_mode == 0:
      self.process_from_folders()
    elif self.parent.work_mode == 1:
      self.process_from_camera()

  def process_from_folders(self):
    if not self.parent.input_folders:
      self.show_warning("Please select at least one input folder.")
      return
    if not self.parent.output_folder:
      self.show_warning("Please select an output folder.")
      return
    if not self.parent.model:
      self.show_warning("Please select a model.")
      return
    if not self.parent.pictures:
      self.show_warning("No pictures to process.")
      return

    for index, original_path in enumerate(self.parent.pictures):
      filename = os.path.splitext(os.path.basename(original_path))[0]
      output_path = os.path.join(self.parent.output_folder, f"processed_{filename}.png")
      proc_time = self.process_image(original_path, output_path)

      self.parent.processing_times.insert(self.parent.current_index, proc_time)
      self.parent.picture_time.setText(f"{self.parent.processing_times[self.parent.current_index]:.2f} s")

      # Update UI
      self.parent.input_pics.append(original_path)
      self.parent.pic1.setPixmap(QPixmap(original_path).scaled(self.parent.pic1.size(), aspectRatioMode=1))
      self.parent.output_pics.append(output_path)
      self.parent.pic2.setPixmap(QPixmap(output_path).scaled(self.parent.pic2.size(), aspectRatioMode=1))
      self.parent.picture_status.setText(f"{index + 1} / {len(self.parent.pictures)}")
      self.parent.current_index = index

      QApplication.processEvents()
      time.sleep(1)

    QMessageBox.information(self.parent, "Success", f"All {len(self.parent.pictures)} pictures have been processed and saved.")

  def process_from_camera(self):
    if not self.parent.camera_info:
      self.show_warning("Please select a camera.")
      return
    if not self.parent.output_folder:
      self.show_warning("Please select an output folder.")
      return
    if not self.parent.model:
      self.show_warning("Please select a model.")
      return
    print("Camera : ", self.parent.camera_info)
    total_index = 0
    self.parent.current_index = 0
    self.parent.input_folder = os.getenv('INPUT_FOLDER_PATH')

    self.camera = self.establish_communication(self.parent.camera_info)
    
    while self.parent.current_index < 9:
      flow_time_start = time.time()
      input_folder = Path(self.parent.input_folder)
      #input_path = os.path.join(self.parent.input_folder, f"image{self.parent.current_index}.png")
      self.take_image(self.parent.camera_info,self.camera)
      images = [f for f in input_folder.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']]
      last_image = max(images, key=lambda f: f.stat().st_mtime)

      input_path = str(last_image.resolve())
      image = cv2.imread(last_image)

      if image is None:
        print("No Image")
        return
      
      image_name = last_image.name
      print(image_name)
      output_path = os.path.join(self.parent.output_folder, f"processed_{image_name}.png")
      self.process_image(input_path, output_path)

      flow_time_end = time.time()
      flow_time_final = flow_time_end - flow_time_start
      self.parent.processing_times.insert(self.parent.current_index, flow_time_final)
      self.parent.picture_time.setText(f"{flow_time_final:.2f} s")

      # Update UI
      self.parent.input_pics.append(input_path)
      self.parent.pic1.setPixmap(QPixmap(input_path).scaled(self.parent.pic1.size(), aspectRatioMode=1))
      self.parent.output_pics.append(output_path)
      self.parent.pic2.setPixmap(QPixmap(output_path).scaled(self.parent.pic2.size(), aspectRatioMode=1))
      total_index += 1
      self.parent.picture_status.setText(f"{self.parent.current_index + 1} / {total_index}")

      self.parent.current_index += 1
      QApplication.processEvents()

    #self.parent.connection.disconnect(self.parent.camera)
    self.parent.input_folders.append(self.parent.input_folder)
    self.parent.load_pictures()
    QMessageBox.information(self.parent, "Success", f"All {total_index} pictures have been processed and saved.")

  def process_image(self, input_path, output_path):
    match self.parent.model:
      case "YOLO":
        return YOLOv11.yolo_detect(input_path, output_path)
      case "Segment by lightening":
        return ImageProcessor.segment_by_lightening(input_path, output_path)
      case "Segment by darkening":
        return ImageProcessor.segment_by_darkening(input_path, output_path)
      case "Segment bin":
        return ImageProcessor.segment_bin(input_path, output_path)
      case "Just take the images":
        return ImageProcessor.just_take_the_image(input_path, output_path)
      case "Segment wooden":
        return ImageProcessor.wooden_pallet(input_path, output_path)
      case "Fast-SAM":
        return ImageProcessor.fast_sam(input_path, output_path)
      case _:
        return ImageProcessor.convert_to_negative(input_path, output_path)

  def establish_communication(self, camera_info):
    cam_processor = CameraProcessor(input_path=self.parent.input_folder)
    if "MechMind" in camera_info:
      return cam_processor.mechmind_connect(camera_info)
    if "Photoneo" in camera_info:
      return cam_processor.photoneo_connect(camera_info)

  def take_image(self, camera_info, camera):
    cam_processor = CameraProcessor(input_path=self.parent.input_folder)
    if "MechMind" in camera_info:
      cam_processor.mechmind_capture(camera, 0)
    if "Photoneo" in camera_info:
      cam_processor.photoneo_capture(camera)
      
