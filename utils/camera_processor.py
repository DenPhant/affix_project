import os
from datetime import datetime
from utils.photoneo.photoneo_control import PhotoneoControl
from utils.mechmind.mechmind_connection import MechmindConnection

class CameraProcessor:
  def __init__(self, input_path):
    if not os.path.exists(input_path):
      raise Exception("Error: The path provided does not exist in the system: \n\
                      " + input_path)
    
    self.path = input_path
  
  def mechmind_capture(self,camera_connection,image_mode=0):
    try:
      
      connection = MechmindConnection()
      now = datetime.now()
      timestamp = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
      name = self.path + "image"+timestamp+".png"
      ##Image Mode:
      # 0 - 2D image
      # 1 - 3D image
      # 2 - 3D with Normal
      # 3 - 2D and 3D
      # 4 - 2D and 3D with Normal
      # 5 - 2D stereo
      match image_mode:
        case 0:
          connection.get_2d_image(camera=camera_connection,file_name=name)
          return name
        #With other cases, ass methods in the Mechmind first
        case 1:
          pass
        case 2:
          pass
        case 3:
          pass
        case 4:
          pass
        case 5:
          pass
        case _:
          raise Exception("""Error: unknown MechMind camera mode, please choose the following:\n" \
                          0 - 2D image  
                          1 - 3D image  
                          2 - 3D with Normal 
                          3 - 2D and 3D
                          4 - 2D and 3D with Normal  
                          5 - 2D stereo""")
    except Exception as ex:
      print(ex)
  
  def mechmind_connect(self, camera_info):
    connection = MechmindConnection()
    info = camera_info.split(" - ")
    #info[0] - Camera Name
    #info[1] - Camera Serial Number
    #info[2] - Camera IP Address
    #info[3] - Camera Brand
    conn = connection.connect(info)
    return conn

  def photoneo_connect(self, camera_info, params = []):
    info = camera_info.split(" - ")
    id = info[1]
    name = info[0]
    type = 0
    if("MotionCam" in name):
      if("Color" in name):
        type = 2
      else:
        type = 1
    #For the demo - remove later
    type = 2
    cti_path = ""
    try:
      connection = PhotoneoControl(id, cti_path, type)
      ia, features = connection.create_image_ground(params=params, mode=1)
      package = {
        "connection" : connection,
        "ia" : ia,
        "features" : features
      }
      ia.start()
      return package

    except Exception as ex:
        raise ex


  
  def photoneo_capture(self, connection, inputs=[], ms=200, mode=1):
    features = connection['features']
    ia = connection['ia']
    if(inputs == []):
      inputs = [self.path]
    try:
      connection['connection'].takeImage(features=features, ia=ia, output_path=inputs, mode=mode, ms=ms)
      return True
    except Exception as ex:
      raise ex
    
      


    