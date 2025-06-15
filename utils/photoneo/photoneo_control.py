import os
from harvesters.core import Harvester
import pandas as pd
import numpy as np
import open3d as o3d
import cv2
from datetime import datetime
from pathlib import Path
from sys import platform
from utils.photoneo.potoneo_connection import PhotoneoConnection

class PhotoneoControl:
  def __init__(self, device_id, cti_path=None, camera_type=0):
    if(cti_path is None or cti_path == ""):
      #Make cti_path default value
      cti_path = os.getenv('PHOXI_CONTROL_PATH') + "/API/bin/photoneo.cti"
    if(device_id is None):
      raise Exception("Error: No device id provided, check your device ID in PhoXi Control app")
    self.device = device_id
    self.cti = cti_path
    if (camera_type < 3 and camera_type >= 0):
      self.type = camera_type
    else:
      raise Exception("Error: Invalid camera type \n " \
                      "Please make sure that camera type follows the defined logic:\n" \
                      "Type:\n" \
                      "0 - Default Photoneo camera\n" \
                      "1 - MotionCam3D camera\n" \
                      "2 - MotionCam3d Color")
    
    #Default parameters in case of empty passes
    self.params = pd.Series({
      "Texture Image" : False,
      "Point Cloud Image" : False,
      "Normal Map Image" : False,
      "Depth Map Image" : False,
      "Confidence Map Image" : False,
      "Events Map Image" : False,
      "Color Camera Image" : True,
    })

  def getType(self):
    return self.type

  def getImageParams(self):
    return self.params
  

  def save_texture_if_available(self,texture_component, filename="texture.png"):
    if texture_component.width == 0 or texture_component.height == 0:
      print("Texture is empty!")
      return

    texture = texture_component.data.reshape(texture_component.height, texture_component.width, 1).copy()
    texture_screen = cv2.normalize(texture, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)
    cv2.imwrite(filename, texture_screen)
    print(f"Saved texture to {filename}")

  def save_color_image_if_available(self,color_component, filename="color_image.png"):
    if color_component.width == 0 or color_component.height == 0:
      print(f"{filename} is empty!")
      return

    color_image = color_component.data.reshape(color_component.height, color_component.width, 3).copy()
    color_image = cv2.normalize(color_image, dst=None, alpha=0, beta=65535, norm_type=cv2.NORM_MINMAX)
    color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
    cv2.imwrite(filename, color_image)
    print(f"Saved color image to {filename}")

  def save_pointcloud_if_available(self,pointcloud_comp, normal_comp, texture_comp, texture_rgb_comp, filename="pointcloud.ply"):
    if pointcloud_comp.width == 0 or pointcloud_comp.height == 0:
      print("PointCloud is empty!")
      return

    pointcloud = pointcloud_comp.data.reshape(pointcloud_comp.height * pointcloud_comp.width, 3).copy()
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(pointcloud)

    if normal_comp and normal_comp.width > 0 and normal_comp.height > 0:
      norm_map = normal_comp.data.reshape(normal_comp.height * normal_comp.width, 3).copy()
      pcd.normals = o3d.utility.Vector3dVector(norm_map)

    texture_rgb = np.zeros((pointcloud_comp.height * pointcloud_comp.width, 3))
    if texture_comp and texture_comp.width > 0 and texture_comp.height > 0:
      texture = texture_comp.data.reshape(texture_comp.height, texture_comp.width, 1).copy()
      norm_texture = 1 / 65536 * texture
      texture_rgb[:, 0] = norm_texture.flatten()
      texture_rgb[:, 1] = norm_texture.flatten()
      texture_rgb[:, 2] = norm_texture.flatten()
    elif texture_rgb_comp and texture_rgb_comp.width > 0 and texture_rgb_comp.height > 0:
      texture = texture_rgb_comp.data.reshape(texture_rgb_comp.height, texture_rgb_comp.width, 3).copy()
      texture_rgb[:, 0] = np.reshape(1 / 65536 * texture[:, :, 0], -1)
      texture_rgb[:, 1] = np.reshape(1 / 65536 * texture[:, :, 1], -1)
      texture_rgb[:, 2] = np.reshape(1 / 65536 * texture[:, :, 2], -1)

    texture_rgb = cv2.normalize(texture_rgb, dst=None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)
    pcd.colors = o3d.utility.Vector3dVector(texture_rgb)

    o3d.io.write_point_cloud(filename, pcd)
    print(f"Saved point cloud to {filename}")
    return

  #Create Harvester object that will serve as image acquirer when required, this is going to establish 
  #Connection between software and camerasensor, once acquirer is closed, connection will be closed as well
  #Use this method after comera connection

  def create_image_ground(self, params, mode):
    conn = PhotoneoConnection(id=self.device, path=self.cti).get_connection()
    print(self.type)
    
    if mode == 1:
      conn["features"].PhotoneoTriggerMode.value = "Software"
    else:
      conn["features"].PhotoneoTriggerMode.value = "Freerun"

    if params == []:
      params = self.params
    print(params[6])
    conn["features"].SendTexture.value = params[0]
    conn["features"].SendPointCloud.value = params[1]
    conn["features"].SendNormalMap.value = params[2]
    conn["features"].SendDepthMap.value = params[3]
    conn["features"].SendConfidenceMap.value = params[4]
    if self.type > 0:
      conn["features"].SendEventMap.value = params[5]
    if self.type > 1:
      conn["features"].SendColorCameraImage.value = params[6]
    return conn["ia"], conn["features"]
  

  #Harvester for configuration change
  #Instead of applying configuration for the image taking, this will only return image acquirer and features
  def create_settings_ground(self):
    print(self.device)
    print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
    print(self.cti)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    
    phocon = PhotoneoConnection(id=self.device, path=self.cti)
    print(phocon.conn)
    conn = phocon.get_connection() 
    return conn["ia"], conn["features"]
  
  def takeImage(self, ia, features, output_path, mode=1, ms=10):
    if (mode != 1 and mode != 2):
      raise Exception(f"Error: Incorrect mode.\n \
                      1 - Single or 2 - Stream expected, but got {mode}")
    try:
      def capture_and_save():
        with ia.fetch(timeout=ms) as buffer:
          #grab newest frame
          #do something with second frame
          payload = buffer.payload
          texture_component = payload.components[0]
          texture_rgb_component = payload.components[7]
          point_cloud_component = payload.components[2]
          norm_component = payload.components[3]
          timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
          if(len(output_path) > 1):
            self.save_texture_if_available(texture_component, output_path[1]+"output_texture"+timestamp+".png")
          self.save_color_image_if_available(texture_rgb_component, output_path[0]+"output_texture_rgb"+timestamp+".png")
          if(len(output_path) > 2):
            self.save_pointcloud_if_available(point_cloud_component, norm_component, texture_component, texture_rgb_component, output_path[3]+"output_pointcloud"+timestamp+".ply")
      if mode == 1:
        features.TriggerFrame.execute()
      capture_and_save()
        
      

    except Exception as e:
      print(e)


  