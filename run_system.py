###
# Final Project for Graphics and Visual Computing Course
###

## The main program
import web_api
import tkinter as tk
from tkinter.ttk import Combobox
from time import strftime
import cv2
import PIL.Image, PIL.ImageTk
import json
import pickle
import time
import threading
import screen_brightness_control as sbc

api = web_api.API()
CamScaleW = 645
CamScaleH = 810

class Flash_Window():
    def __init__(self):
        self.ww = tk.Toplevel()
        self.ww.attributes("-fullscreen", True)
        # self.ww.configure(bg='blue')

class Notifcation_Window():
    def __init__(self, window, window_title, input_text):
        self.ww = window
        self.ww.title(window_title)
        self.ww.geometry("200x200+300+100")
        self.ww.resizable(width=False, height=False)

        self.text = tk.Label(window, text=input_text, font=('Montserrat', 10, 'regular'))
        self.text.place()

class App:

    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.window.geometry(str(CamScaleW)+"x"+ str(CamScaleH) +"+300+100")
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
        self.id_label = tk.Label(window, text='Class Schedule', font=('Montserrat', 12, 'bold'))
        self.id_label.grid(row=2, column=0, columnspan=2, sticky='S' )
        self.cBoxData = self.ClassSched()
        self.cb = Combobox(window, values=self.cBoxData)
        self.cb.grid(row=3, column=0, columnspan=2, ipadx=100, ipady=5, pady=15)

        # employee ID input
        self.id_label = tk.Label(window, text='Faculty ID', font=('Montserrat', 12, 'bold'))
        self.id_label.grid(row=4, column=0, columnspan=2, sticky='S' )
        self.eID = tk.Entry(window, bd=2)
        self.eID.grid(row=5, column=0, columnspan=2, ipadx=110, ipady=5, )

        # Button that lets the user take a snapshot
        self.attend = tk.Button(window, text="Log Attendance", fg='white', bg='#0034D1', command=self.CheckAttendance)
        self.attend.grid(row=6, column=0, sticky='e', ipadx=75, ipady=5, pady=10, padx=5)

        # quit button
        self.btn_quit = tk.Button(window, text='Exit', fg='white', bg='#0034D1', command=quit)
        self.btn_quit.grid(row=6, column=1, sticky='w', ipadx=25, ipady=5, pady=10, padx=5)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()
        window.mainloop()

    # function to be called that checks the empID input when attendance button is clicked
    def CheckAttendance(self):
        def flashbang():
            curr_brightness = 60
            flash = Flash_Window()
            sbc.set_brightness(100)
            time.sleep(0.2)

            # get id input
            self.inputID = self.eID.get()
            print(self.inputID)

            sbc.set_brightness(curr_brightness)
            flash.ww.destroy()

            print(api.check_if_account_exists(id=1653206499))  # test

        def checkClassSched():
            pass


        flash_thread = threading.Thread(target=flashbang)
        flash_thread.start()


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
        with open('ClassCodes.json') as json_file:
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

            ret, fr = self.vid.read()
            self.edge_detection(frame=fr)
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (None, None)

# added by Bohol, Christopher
    def edge_detection(self, frame):
        path = "cascades\\data\\haarcascade_frontalface_alt_tree.xml"
        face_cascade = cv2.CascadeClassifier(path)

        # added and edited by Gadiane, James Christian
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trained.yml")
        with open("labels.pkl", 'rb') as f:
            main_labels = pickle.load(f)
            labels = {v: k for k, v in main_labels.items()}

        HSV_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        YCbCr_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
        LUV_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2LUV)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #converting frame to grayscale
        HSV_cv = cv2.cvtColor(HSV_cv, cv2.COLOR_BGR2GRAY)
        YCbCr_cv = cv2.cvtColor(YCbCr_cv, cv2.COLOR_BGR2GRAY)
        LUV_cv = cv2.cvtColor(LUV_cv, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1, minNeighbors=5) #detecting faces in the frame
        # edges = cv2.Canny(gray_frame, 100, 200) #generating edge map using Canny Edge Detector

        font = cv2.FONT_HERSHEY_SIMPLEX
        fScale = (CamScaleW * CamScaleH) / (900 * 900)
        stroke = 2
        for(x,y,w,h) in faces:
            point = (x, y)
            # print(x,y,w,h)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), stroke)
            roi_gray = gray_frame[y:y+h, x:x+w] #cropping the face
            HSV_frame = HSV_cv[y:y+h, x:x+w]
            YCbCr_frame = YCbCr_cv[y:y+h, x:x+w]
            LUV_frame = LUV_cv[y:y+h, x:x+w]

            id_1, conf1 = recognizer.predict(roi_gray)
            id_2, conf2 = recognizer.predict(HSV_frame)
            id_3, conf3 = recognizer.predict(YCbCr_frame)
            id_4, conf4 = recognizer.predict(LUV_frame)

            if conf4 >= 40 and conf4 <= 80:
                print("LUV!!")
                # print(labels[id_])
                self.name = labels[id_4]
                color = (255, 255, 255)
                cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
                # cv2.putText(frame, name, (x,y), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2) #BY: Bohol
            elif conf3 >= 40 and conf3 <= 80:
                print("YCbCr!!!!")
                self.name = labels[id_3]
                color = (255, 255, 255)
                cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
            elif conf2 >= 40 and conf2 <= 80:
                print("HSV!!")
                self.name = labels[id_2]
                color = (255, 255, 255)
                cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
            elif conf1 >= 40 and conf1 <= 80:
                print("grayscale!!")
                self.name = labels[id_1]
                color = (255, 255, 255)
                cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
            else:
                name = "False"
                color = (0, 0, 255)
                cv2.putText(frame, name, point, font, 1, color, stroke, cv2.LINE_AA)
                cv2.rectangle(frame, point, (x + w, y + h), color, stroke)
            # drawing rectangle around the face

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
    main_th = threading.Thread(target=main)
    main_th.start()
