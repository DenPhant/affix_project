import sys
from PyQt5.QtWidgets import QApplication
from head_gui import GeneralWindow
import json
import subprocess
import os

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

config_path = "config.json"

def load_config():
    if not os.path.exists(config_path):
        
        default_config = {
            "env": {"setup": {"complete": False}},
            "dependencies": []
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
        return default_config
    else:
        
        with open(config_path, "r") as f:
            return json.load(f)


def save_config(config):
    with open(config_path, "w") as f:
        json.dump(config, f, indent=4)


def setup_environment():
    
    config = load_config()
    setup_complete = config.get("env", {}).get("setup", {}).get("complete", False)
    required_packages = config.get("dependencies", [])

    if not required_packages:
        print("No dependencies listed in config.json. Add required packages to the 'dependencies' list.")
        return

    if not setup_complete:
        print("Environment setup not complete. Installing required packages...")
        for package in required_packages:
            try:
                print(f"Installing {package}...")
                install(package)
            except Exception as e:
                print(f"Failed to install {package}: {e}")
            else:
                print(f"{package} installed successfully!")

        
        config["env"]["setup"]["complete"] = True
        save_config(config)
        print("Environment setup completed!")
    else:
        print("Environment setup is already complete.")
      
if __name__ == "__main__":
    setup_environment()
    app = QApplication(sys.argv)
    main_window = GeneralWindow()
    main_window.show()
    sys.exit(app.exec_())
