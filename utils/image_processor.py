import os
import cv2
import time
import numpy as np
from skimage.segmentation import watershed
from skimage.feature import peak_local_max
from scipy import ndimage
from skimage.measure import label, regionprops
from skimage import io
from skimage.filters import threshold_otsu
from skimage.segmentation import clear_border
from skimage.measure import label, regionprops
from skimage.morphology import closing, square, opening, footprint_rectangle
from skimage.color import label2rgb
from utils.models.fast_sam.FastSAM import FastSAMSegmenter

class ImageProcessor:
    
    
    #Example of a static method, mock method for processing unknown/not implemented type images
    @staticmethod
    def convert_to_grayscale(input_path, output_path):
      try:
        start_time = time.time()
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
          raise ValueError(f"Invalid image path: {input_path}")
        cv2.imwrite(output_path, image)
        end_time = time.time()
        processing_time = end_time - start_time
        return processing_time
      except Exception as e:
        print(f"Error processing image {input_path}: {e}")



    @staticmethod
    def segment_by_lightening(input_path, output_path):
      try:
        start_time = time.time()
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
          raise ValueError(f"Invalid image path: {input_path}")
        cropped_image = image[200:1100, 350:1500]
        adjusted_image = cv2.convertScaleAbs(cropped_image, alpha=3, beta=20)

        #Apply Otsu's thresholding
        _, binary_image = cv2.threshold(adjusted_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        #Morphological closing to fill small holes (kernel size 3x3)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        #Remove artifacts connected to the image border
        cleared_image = cv2.copyMakeBorder(closed_image, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        contours, _ = cv2.findContours(cleared_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #Create overlay for visualization by drawing contours on the original image
        overlay = cv2.cvtColor(adjusted_image, cv2.COLOR_GRAY2BGR)
        cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)
        
        #Save the overlay image
        cv2.imwrite(output_path, overlay)
        end_time = time.time()
        processing_time = end_time - start_time
        return processing_time
      except Exception as e:
        print(f"Error processing image {input_path}: {e}")
    


    @staticmethod
    def convert_to_negative(input_path, output_path):
      try:
        start_time = time.time()
        image = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        if image is None:
          raise ValueError(f"Invalid image path: {input_path}")
        negative_image = cv2.bitwise_not(image)
        cv2.imwrite(output_path, negative_image)
        end_time = time.time()
        processing_time = end_time - start_time
        return processing_time
      except Exception as e:
        print(f"Error processing image {input_path}: {e}")



    @staticmethod
    def segment_by_darkening(input_path, output_path):
      try:
        start_time = time.time()
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
          raise ValueError(f"Invalid image path: {input_path}")
        cropped_image = image[100:1000, 100:1500]
        adjusted_image = cv2.convertScaleAbs(cropped_image, alpha=3, beta=20)

        #Apply Otsu's thresholding
        _, binary_image = cv2.threshold(adjusted_image, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        #Morphological closing to fill small holes (kernel size 3x3)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

        #Remove artifacts connected to the image border
        cleared_image = cv2.copyMakeBorder(closed_image, 1, 1, 1, 1, cv2.BORDER_CONSTANT, value=0)
        contours, _ = cv2.findContours(cleared_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #Create overlay for visualization by drawing contours on the original image
        overlay = cv2.cvtColor(adjusted_image, cv2.COLOR_GRAY2RGB)
        cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)
        
        #Save the overlay image
        cv2.imwrite(output_path, overlay)
        end_time = time.time()
        processing_time = end_time - start_time
        return processing_time
      except Exception as e:
        print(f"Error processing image {input_path}: {e}")
        
    @staticmethod
    def wooden_pallet(input_path, output_path):
      try:
        start_time = time.time()
        image = cv2.imread(input_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        if image is None:
            raise ValueError("Image not found or could not be loaded.")
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Edge detection (Canny is good for outlines)
        edges = cv2.Canny(blurred, threshold1=50, threshold2=150)

        # Find contours based on edges
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw contours on a copy of the original image
        outlined_image = image.copy()
        cv2.drawContours(outlined_image, contours, -1, (0, 255, 0), 2)

        # Save and show result
        cv2.imwrite(output_path, outlined_image)
        print(f"Outlined image saved as: {output_path}")
        end_time = time.time()
        processing_time = end_time - start_time
        return processing_time
      except Exception as e:
        print(f"Error processing image {input_path}: {e}")

    @staticmethod
    def segment_bin(input_path, output_path):
      try:
        start_time = time.time()
        image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
        if image is None:
          raise ValueError(f"Invalid image path: {input_path}")
        
        cropped_image = image[10:1300, 10:1400]
        
        
        blurred = cv2.GaussianBlur(cropped_image, (5, 5), 0)
        
        #Thresholding - Otsu's method
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        #Noise removal with morphological operations
        #Array of 3x3 matrix of ones of uint8 type
        kernel = np.ones((3, 3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        #Sure background area
        sure_bg = cv2.dilate(opening, kernel, iterations=3)
        
        # Finding sure foreground area using distance transform
        dist_transform = cv2.distanceTransform(opening, cv2.DIST_L2, 5)
        _, sure_fg = cv2.threshold(dist_transform, 0.5 * dist_transform.max(), 255, 0)
        sure_fg = np.uint8(sure_fg)
        
        #Finding unknown region
        unknown = cv2.subtract(sure_bg, sure_fg)
        
        #Marker labelling
        _, markers = cv2.connectedComponents(sure_fg)
        
        #Add one to all labels so that sure background is not 0, but 1
        markers = markers + 1
        
        #Now, mark the region of unknown with zero
        markers[unknown == 255] = 0
        
        #Apply watershed algorithm
        markers = watershed(-dist_transform, markers, mask=opening)
        
        #Create output image with contours
        output = cropped_image.copy()
        
        #Loop over the unique labels returned by the Watershed algorithm
        for label in np.unique(markers):
          if label < 1:  #Skip the background
            continue
                
          # Create a mask for the current label
          mask = np.zeros(cropped_image.shape, dtype="uint8")
          mask[markers == label] = 255
          
          # Find contours in the mask
          contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
          
          # Draw the contour on the output image
          output = cv2.cvtColor(thresh, cv2.COLOR_GRAY2BGR)

          # Draw contours in green
          cv2.drawContours(output, contours, -1, (0, 255, 0), 2)

        # Save the image with contours
        cv2.imwrite(output_path, output)
        end_time = time.time()
        processing_time = end_time - start_time
        return processing_time
      except Exception as e:
        print(f"Error processing image {input_path}: {e}")

    @staticmethod
    def just_take_the_image(input_path, output_path):
      try:
        start_time = time.time()
        image = cv2.imread(input_path)
        if image is None:
          raise ValueError(f"Invalid image path: {input_path}")
        cropped_image = image[300:950, 250:1050]
        cv2.imwrite(output_path, cropped_image)
        end_time = time.time()
        processing_time = end_time - start_time
        return processing_time
      except Exception as e:
        print(f"Error processing image {input_path}: {e}")

    #We just use this methods for experiment, safe to delete        
    @staticmethod
    def test_image_processor(input_path, output_path):
      import os
      from skimage.filters import threshold_otsu
      from skimage.morphology import closing, rectangle
      from skimage.measure import label
      from skimage.color import label2rgb
      
      start_time = time.time()
      
      # Load the image
      image = cv2.imread(input_path, cv2.IMREAD_GRAYSCALE)
      if image is None:
          raise ValueError(f"Failed to load image from {input_path}")
      
      # Adjust and crop the image
      adjusted_image = cv2.convertScaleAbs(image, alpha=3, beta=20)
      cropped_image = adjusted_image[500:900, 650:1300]
      
      # Apply threshold
      thresh = threshold_otsu(cropped_image)
      print(f"Threshold value: {thresh}")
      bw = closing(cropped_image > thresh, rectangle(3, 3))
      
      if bw is None or bw.size == 0:
          raise ValueError("Binary image is empty after processing!")
      
      # Label image regions
      label_image = label(bw)
      print(f"Label image shape: {label_image.shape}")
      
      # Overlay labels on the original image
      image_label_overlay = label2rgb(label_image, image=cropped_image, bg_label=0)
      
      # Save the binary image
      if not os.path.isdir(os.path.dirname(output_path)):
          raise ValueError(f"Output directory does not exist: {os.path.dirname(output_path)}")
      
      cv2.imwrite(output_path, image_label_overlay)
      print(f"Processed image saved to {output_path}")
      
      end_time = time.time()
      processing_time = end_time - start_time
      return processing_time
    
    @staticmethod
    def fast_sam(input_path, output_path):
      print(output_path)
      sam = FastSAMSegmenter(input_path, output_path)
      try:
        proc_time = sam.segment()
        return proc_time
      except Exception as ex:
        raise Exception(ex)


