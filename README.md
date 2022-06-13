# Image-Facial-Recognition-Attendance-System

##Finals Project Requirement
###for Graphics and Visual Computing 11053

- University of San Jose-Recoletos
- School of Computer Sciences
- Basak, Cebu City, Philippines

>The primary goal of the project is to record attendances by using computer vision 
as daily use in one university faculty. Taking advantage of human-computer interaction 
in order to reduce use case errors during a faculty member’s attendance when they 
enter a class. 

Before testing to run this repo, here are some requirements needed:

1. Create an empty folder (images) inside the repo where you will store your own face datasets
2. 



>Datasets used in this project are 1,606 images of Person and Picture_frame labels from 'Open Image'.
Which are completely trained from Roboflow and Google Colab. 

You can choose any of the models being trained, with different set parameters (v3 is the recommended trained model with 50 epochs and 40 batches) 
```
Image-Facial-Recognition-Attendance-System/object_detect_model/best_custom_open_image v3.pt
```
Just feel free to modify Detector.py and insert your own custom object detection model
```
line 10: self.modelPath = os.path.join("object_detect_model", "best_custom_open_image v3.pt")
```


