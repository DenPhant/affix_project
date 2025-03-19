import cv2
import numpy as np

from mecheye.shared import *
from mecheye.area_scan_3d_camera import *
from mecheye.area_scan_3d_camera_utils import *



class MechmindConnection:
  #Parameter converter, the parameters we get from camera have enum, here is explanation of that enum,
  #More broad explanation is in official odcumentation - https://docs.mech-mind.net/api-reference/eye-api-camera-cpp/2.4.1/index.html
  def convert_parameter(self, type):
    if type == 0:
      return "INT"
    elif type == 1:
      return "FLOAT"
    elif type == 2:
      return "BOOL"
    elif type == 3:
      return "ENUM"
    elif type == 4:
      return "ROI (Region of Interest)"
    elif type == 5:
      return "RANGE"
    elif type == 6:
      return "FLOAT ARRAY (Vector of double types)"
    elif type == 7:
      return "ROI ARRAY (Vector of ROI types)"
    elif type == 8:
      return "PROFILE ROI (ROI of lazer profiler)"
    else:
      return "UNKNOWN"
    
  def find_cameras(self):
    camera = Camera()
    #List of CameraInfo objects
    info_list = camera.discover_cameras()
    if len(info_list) == 0:
      print("No cameras found") 
    return info_list
  
  def connect(self, camera_info):
    camera = Camera()
    #List of CameraInfo objects
    info_list = camera.discover_cameras()
    if len(info_list) == 0:
      print("No cameras found") 
    for info in info_list:
       print("Camera found: ", info)
    try:
      camera.connect(camera_info.ip_address)
      print("Successfyully connected to the camera ",camera_info.model)
      return camera
    except:
      print("Failed to connect to the camera")
      return

  def get_2d_image(self, camera, file_name):
    try:
      frame_2d = Frame2D()
      camera.capture_2d(frame_2d)
      color = frame_2d.get_color_image()

      if color is None:
        print("Failed to get color image")
        return
      
      #Save the image
      #print(color.data())
      try:
        cv2.imwrite(file_name, color.data())
      except:
        color_copy = np.uint8(color.data())
        cv2.imwrite(file_name, color_copy)
    except Exception as e:
      print("Failed to get 2D image", e)
      return
    
  def disconnect(self, camera):
    try:
      camera.disconnect()
      print("Camera disconnected")
    except:
      print("Failed to disconnect the camera")
    return

  def view_settings(self, camera):
    try:
      user_manager = camera.user_set_manager()
      error, user_sets = user_manager.get_all_user_set_names()
      if error.error_code != 0:
        print(error.error_code)
        print("Failed to get user sets")
        return
      #Print sets to know how do they look
      for user_set in user_sets:
        print(user_set)
      print("___________________________________")
      user_manager.select_user_set(user_sets[0])

      current_set = camera.current_user_set()
      parameters = current_set.get_available_parameters()
      
      #Print parameters to know how do they look
      for parameter in parameters:
        type_expl = self.convert_parameter(parameter.type())
        print(parameter.name())
        print("Type - ",parameter.type(),", ", type_expl)
        print(parameter.description())
        print("Writable - ", parameter.is_writable())
        print("Readable - ", parameter.is_readable())
        print("___________________________________")

      #For the demo purposes - just show the parameter
      error, fringe_contrast_threshold = current_set.get_int_value(PointCloudFringeContrastThreshold.name)
      if error.error_code != 0:
        print(error.error_code)
        print("Failed to get fringe contrast threshold")
        #return
      
      print("Fringe contrast threshold: ", fringe_contrast_threshold)
    except:
      print("Issue with user set manager")

  