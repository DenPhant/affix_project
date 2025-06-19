from harvesters.core import Harvester
import os
class PhotoneoConnection:
  _instance = None
  def __new__(cls, id, path=None, *args, **kwargs):
    if cls._instance is None:
      print("Creating new connection")
      cls._instance = super().__new__(cls)
      cls._instance.connect(id=id, cti_path=path)
    return cls._instance
    
  def connect(self, id, cti_path = None):
    # Your actual connection logic
    h = Harvester()
    if cti_path is None or cti_path == "":
      cti_path = os.getenv('PHOXI_CONTROL_PATH') + "/API/bin/photoneo.cti"
    h.add_file(cti_path, True, True)
    h.update()
    ia = h.create({'id_':id})
    #Add CTI file and check its validity
    features = ia.remote_device.node_map
    self.conn = {
      "ia" : ia,
      "features" : features
    }

  def get_connection(self):
    return self.conn