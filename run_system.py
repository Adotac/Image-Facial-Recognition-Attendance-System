###
# Final Project for Graphics and Visual Computing Course
###

## The main program
import tkinter as tk
from tkinter.ttk import Combobox
from time import strftime
from turtle import color
import cv2
import PIL.Image, PIL.ImageTk
import json
import os
import pickle

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("645x730+300+100")
        self.window.resizable(width=False, height=False)
        self.video_source = video_source
        self.ok = False

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)
        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=640, height=480)
        self.canvas.grid(row=0, column=0, columnspan=2)

        self.timeDate = tk.Label(window, font=('Montserrat', 18, 'bold'), bg='#c4c4c4')
        self.timeDate.grid(row=1, column=0, columnspan=2, sticky='ew', ipady=15)
        self.TimeDate()

        # A combo box to choose what class you're trying to check attendance to
        self.cBoxData = self.ClassSched()
        self.cb = Combobox(window, values=self.cBoxData)
        self.cb.grid(row=2, column=0, columnspan=2, ipadx=100, ipady=5, pady=15)

        # employee ID input
        self.eID = tk.Entry(window, bd=2)
        self.eID.grid(row=3, column=0, columnspan=2, ipadx=110, ipady=5, )

        # Button that lets the user take a snapshot
        self.attend = tk.Button(window, text="Log Attendance", fg='white', bg='#0034D1', command=self.CheckAttendance)
        self.attend.grid(row=4, column=0, sticky='e', ipadx=75, ipady=5, pady=10, padx=5)

        # quit button
        self.btn_quit = tk.Button(window, text='Exit', fg='white', bg='#0034D1', command=quit)
        self.btn_quit.grid(row=4, column=1, sticky='w', ipadx=25, ipady=5, pady=10, padx=5)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()
        window.mainloop()


    # function to be called that checks the empID input when attendance button is clicked
    def CheckAttendance(self):
        self.inputID = self.eID.get()
        print(self.inputID)

    def update(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.window.after(self.delay, self.update)

    def TimeDate(self):
        time_string = strftime('%H:%M:%S %p \n %A, %x')  # time format
        self.timeDate.config(text=time_string)
        self.timeDate.after(1000, self.TimeDate)  # time delay of 1000 milliseconds

    def ClassSched(self):
        with open(dir_path + '/' + 'ClassCodes.json') as json_file:
            self.codes = json.load(json_file)
            self.temp = list()
            for i in self.codes:
                self.temp.append(self.codes[i]['classCode'] + " " +
                                 self.codes[i]['altName'] + " " +
                                 self.codes[i]['classDays'] + " " +
                                 str(self.codes[i]['classStart']['hr']) + ":" + str(self.codes[i]['classStart']['min']) + " " + self.codes[i]['classStart']['p'])

        return tuple(self.temp)



class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    # To get frames
    def get_frame(self):
        if self.vid.isOpened():

            ret, frame = self.vid.read()
            self.edge_detection(frame=frame)
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (None, None)

# added by Bohol, Christopher
    def edge_detection(self, frame):
        path = "cascades\data\haarcascade_frontalface_default.xml"
        face_cascade = cv2.CascadeClassifier(path)

        # added and edited by Gadiane, James Christian
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trained.yml")
        with open("labels.pickle", 'rb') as f:
            main_labels = pickle.load(f)
            labels = {v: k for k, v in main_labels.items()}

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #converting frame to grayscale
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.05, minNeighbors=5) #detecting faces in the frame
        edges = cv2.Canny(gray_frame, 100, 200) #generating edge map using Canny Edge Detector
        for(x,y,w,h) in faces:
            # print(x,y,w,h)
            roi_gray = gray_frame[y:y+h, x:x+w] #cropping the face
            roi_color = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            id_, conf = recognizer.predict(roi_gray)
            if conf >= 40 and conf <= 85:
                print(id_)
                print(labels[id_])
                font = cv2.FONT_HERSHEY_SIMPLEX
                name = labels[id_]
                color = (255, 255, 255)
                stroke = 2
                cv2.putText(frame, name, (x, y), font, 1, color, stroke, cv2.LINE_AA)
                # cv2.putText(frame, name, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) #BY: Bohol
            # drawing rectangle around the face

            # img_itm = "my_im.png"
            # cv2.imwrite(img_itm, roi_gray) #saving the cropped face

            # cv2.imshow('frame', frame)
            # cv2.imshow('gray', roi_gray)

            # cv2.imshow('result', edges) #displaying result (args: Name, Image to show)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            cv2.destroyAllWindows()


def main():
    # Create a window and pass it to the Application object
    App(tk.Tk(), 'Attendance System')


if __name__ == "__main__":
    main()
