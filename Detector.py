import cv2
import numpy as np
import time
import os

class Detector:
    def __init__(self, videopath):
        self.configPath = os.path.join("object_detect_model", "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt")
        self.modelPath = os.path.join("object_detect_model", "frozen_inference_graph.pb")
        self.classesPath = os.path.join("object_detect_model", "coco.names")
        self.videoPath = videopath

        self.net = cv2.dnn_DetectionModel(self.modelPath, self.configPath)
        self.net.setInputSize(size=(320, 320))
        self.net.setInputScale(scale=(1.0/127.5))
        self.net.setInputMean(mean=(127.5, 127.5, 127.5))
        self.net.setInputSwapRB(swapRB=True)

        self.readClasses()

    def readClasses(self):
        with open(self.classesPath, 'r') as f:
            self.classesList = f.read().splitlines()

        self.classesList.insert(0, '__Background__')
        # print(self.classesList)

        self.colorList = np.random.uniform(low=0, high=255, size=(len(self.classesList), 3))


