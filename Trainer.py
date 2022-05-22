import cv2
import os
import numpy as np
from PIL import Image
import pickle
import yaml


def trainLabel_yml():
	folder = os.path.dirname(os.path.abspath(__file__))
	image_files = os.path.join(folder, "images")

	cpath = "cascades\data\haarcascade_frontalface_default.xml"
	casc = cv2.CascadeClassifier(cpath)
	recognizer = cv2.face.LBPHFaceRecognizer_create()

	current_id = 0
	label_ids = {}
	y_labels = []
	x_train = []

	for root, dirs, files in os.walk(image_files):
		for file in files:
			if file.endswith("png") or file.endswith("jpg"):
				path = os.path.join(root, file)
				label = os.path.basename(root).replace(" ", "-").lower()
				if not label in label_ids:
					label_ids[label] = current_id
					current_id += 1
				id_ = label_ids[label]
				pil_image = Image.open(path).convert("L")
				size = (300, 300)
				final_image = pil_image.resize(size, Image.ANTIALIAS)
				image_array = np.array(final_image, "uint8")
				faces = casc.detectMultiScale(image_array, scaleFactor=1.5, minNeighbors=5)

				for (x, y, w, h) in faces:
					roi = image_array[y:y + h, x:x + w]
					x_train.append(roi)
					y_labels.append(id_)

	with open("labels.pkl", 'wb') as f:
		pickle.dump(label_ids, f)

	recognizer.train(x_train, np.array(y_labels))
	recognizer.save("trained.yml")


def test():
	with open("replay-attack_ycrcb_luv_extraTreesClassifier.pkl", 'rb') as f:
		try:
			while True:
				return pickle.load(f)
		except EOFError:
			pass


def load(path):
	pass

if __name__ == "__main__":
	trainLabel_yml()
	for item in test():
		print(repr(item))
