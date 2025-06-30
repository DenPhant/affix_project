# Affix Engineering WP6 - Bin Picking project
This repository hold a code for the machine vision GUI. 
The current verion is a prototype version, incomplete and not secure.

## Recommendation:
+ Python version 11 (With verion 12+, the YOLO Deep Learning model can cause errors)
+ Keep the structure as close as possible to this:
  ![C4](https://github.com/user-attachments/assets/a0d91296-acaa-428f-8ecc-61149b8e3e2f)


## Good to know:
+ This is a prototype, so not bugs will be 100%
+ When Adding a new model, you need to add it in 2 places:
  1. config.jsom
  2. Processor in start_processing() method
+ If you set up env.setup.complete to FALSE in config.json, it will install the dependencies, that will save you time
+ Not all libraries got added to config.json or requirements.txt
+ Check .env.example
+ If you going to use CUDA, please verify your cuda version (*nvcc --version*) and pick appropriate pytorch installation (https://pytorch.org/get-started/locally/) 
+ The GIT branching strategy can be found in project plan or here:
  ![image](https://github.com/user-attachments/assets/ffba0148-acfa-47ab-9234-22da053e7e3b)

### If any question appears, do not hesitate not contacting me! )
