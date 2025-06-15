import torch
import torchvision.transforms.functional as TF
import cv2
import numpy as np
import time
from fastsam import FastSAM
import os

class FastSAMSegmenter:
  model = None

  def __init__(self, input_path, output_path, checkpoint_path=os.getenv('FASTSAM_CHECKPOINT'), model_path=os.getenv('FASTSAM_MODEL_PATH')):
    self.input_path = input_path
    self.output_path = output_path
    self.checkpoint_path = checkpoint_path
    self.model_path = model_path
    self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if FastSAMSegmenter.model is None:
      FastSAMSegmenter.model = self._load_model()
    
    self.sam = FastSAMSegmenter.model

  def _load_model(self):
    sam = FastSAM(self.model_path)
    model = sam.model
    try:
      state_dict = torch.load(self.checkpoint_path, map_location=self.device)
      model.load_state_dict(state_dict)
      print("✅ Fine-tuned checkpoint loaded successfully.")
    except Exception as e:
      print(f"⚠️ Could not load fine-tuned checkpoint. Using default weights.\n{e}")
    model.to(self.device).eval()
    return sam

  def segment(self, imgsz=1120, conf=0.5, iou=0.9):
    try:
      start_time = time.time()

      image = cv2.imread(self.input_path)
      if image is None:
        raise ValueError(f"Image not found: {self.input_path}")

      image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
      image_cropped = image_rgb[90:1000, 140:1600]
      resized_stretched = cv2.resize(image_cropped, (1024, 1024), interpolation=cv2.INTER_LINEAR)
      temp_path = "/utils/models/fast_sam/temp_preprocessed.jpg"
      cv2.imwrite(temp_path, resized_stretched)

      results = self.sam(
        temp_path,
        device=self.device,
        retina_masks=True,
        imgsz=imgsz,
        conf=conf,
        iou=iou
      )

      if not results or not hasattr(results[0], 'masks'):
        print("No masks found in FastSAM output.")
        cv2.imwrite(self.output_path, resized_stretched)
        end_time = time.time()
        return end_time - start_time

      masks = results[0].masks.data
      np.random.seed(42)
      colors = np.random.randint(0, 255, size=(masks.shape[0], 3), dtype=np.uint8)

      overlay = resized_stretched.copy()
      image_cropped = resized_stretched.copy()

      for i, single_mask in enumerate(masks):
        mask_np = single_mask.cpu().numpy().astype(np.uint8) * 255
        resized_mask = cv2.resize(mask_np, (image_cropped.shape[1], image_cropped.shape[0]), interpolation=cv2.INTER_NEAREST)

        color = colors[i]
        color_mask = np.zeros_like(image_cropped, dtype=np.uint8)
        for c in range(3):
          color_mask[:, :, c] = resized_mask * (color[c] / 255)

        alpha = 0.6
        mask_region = resized_mask > 0
        overlay[mask_region] = (
          alpha * color_mask[mask_region] + (1 - alpha) * image_cropped[mask_region]
        ).astype(np.uint8)

      cv2.imwrite(self.output_path, overlay)
      end_time = time.time()
      return end_time - start_time

    except Exception as e:
      print(f"❌ Error processing image {self.input_path}: {e}")
      return None
