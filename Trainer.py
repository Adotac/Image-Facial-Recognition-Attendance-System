import cv2
import os
import numpy as np
from PIL import Image
import pickle
import time

class TrainerLabel_yml():
	def __init__(self):
		self.folder = os.path.dirname(os.path.abspath(__file__))
		self.image_files = os.path.join(self.folder, "images")

		self.cpath = "cascades\data\haarcascade_frontalface_default.xml"
		self.casc = cv2.CascadeClassifier(self.cpath)
		self.recognizer = cv2.face.LBPHFaceRecognizer_create()

		self.current_id = 0
		self.label_ids = {}
		self.y_labels = []
		self.x_train = []

		for root, dirs, files in os.walk(self.image_files):
			for file in files:
				if file.endswith("png"):
					self.color_space_module(ext=".png", _root=root, _dirs=dirs, _file=file)
				elif file.endswith("jpg"):
					self.color_space_module(ext=".jpg", _root=root, _dirs=dirs, _file=file)

		with open("labels.pkl", 'wb') as f:
			pickle.dump(self.label_ids, f)

		self.recognizer.train(self.x_train, np.array(self.y_labels))
		self.recognizer.save("trained.yml")

	##############----------------------------------------##############

	def detect(self, image_array, _id_):
		faces = self.casc.detectMultiScale(image_array, scaleFactor=1.5, minNeighbors=5)

		for (x, y, w, h) in faces:
			roi = image_array[y:y + h, x:x + w]
			self.x_train.append(roi)
			self.y_labels.append(_id_)

	def color_space_module(self, ext, _root, _dirs, _file):
		path = os.path.join(_root, _file)
		temp_img = cv2.imread(path, cv2.IMREAD_COLOR)
		temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB)
		_size = (300, 300)

		label = os.path.basename(_root).replace(" ", "-").lower()

		if not label in self.label_ids:
			self.label_ids[label] = self.current_id
			self.current_id += 1
		id_ = self.label_ids[label]

		###################################################
		# Convert images to various color spaces and turn into grayscale
		###################################################

		HSV_cv = cv2.cvtColor(temp_img, cv2.COLOR_RGB2HSV)
		YCbCr_cv = cv2.cvtColor(temp_img, cv2.COLOR_RGB2YCrCb)

		HSV_cv = cv2.cvtColor(HSV_cv, cv2.COLOR_BGR2GRAY)
		YCbCr_cv = cv2.cvtColor(YCbCr_cv, cv2.COLOR_BGR2GRAY)


		##-------Convert CV2 Grayscales into PIL images------##
		HSV_pil = Image.fromarray(HSV_cv)
		YCbCr_pil = Image.fromarray(YCbCr_cv)

		########-------------------------------#########

		final_HSV = HSV_pil.resize(_size, Image.ANTIALIAS)
		final_YCbCr = YCbCr_pil.resize(_size, Image.ANTIALIAS)

		##############----------------------------------------##############

		HSV_array = np.array(final_HSV, "uint8")
		YCbCr_array = np.array(final_YCbCr, "uint8")

		self.detect(HSV_array, id_)
		self.detect(YCbCr_array, id_)


if __name__ == "__main__":
	start_time = time.process_time()
	run = TrainerLabel_yml()  # Run training and generate model
	print(time.process_time() - start_time, "seconds")

