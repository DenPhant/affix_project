import torch #Computer Vision Machine Learning library
import cv2 #Image Processing library
import numpy as np
import matplotlib.pyplot as plt
from segment_anything import SamPredictor, sam_model_registry, SamAutomaticMaskGenerator
from IPython.display import Image #Display the images
import tifffile
from patchify import patchify
from pathlib import Path
import os
from dotenv import load_dotenv
import time
from PIL import Image
from scipy import ndimage
from IPython.display import display, Markdown, clear_output

#Load environment
load_dotenv()

#TODO: not enough time to finish, continue or delete

DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
MODEL_TYPE = "vit_b"
CHECKPOINT_PATH = os.getenv("SAM_MODEL_PATH")

sam = sam_model_registry[MODEL_TYPE](checkpoint=CHECKPOINT_PATH)
sam.to(device=DEVICE)
predictor = SamPredictor(sam)
mask_generator = SamAutomaticMaskGenerator(sam)

