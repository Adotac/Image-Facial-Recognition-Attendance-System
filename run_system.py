###
# Final Project for Graphics and Visual Computing Course
###

## The main program
import tkinter as tk
from tkinter.ttk import Combobox
from time import strftime
import cv2
import PIL.Image, PIL.ImageTk
import json

class App:
    def __init__(self, window, window_title, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.window.geometry("1000x520+300+100")
        # self.window.resizable(width=False, height=False)
        self.video_source = video_source
        self.ok = False

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)
        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(window, width=640, height=480)
        self.canvas.pack(side=tk.LEFT)

        # Display real time clock
        self.timeDate = tk.Label(window, font=('times', 26, 'bold'), bg='yellow')
        self.timeDate.place(x=645, y=10, width=350)
        self.TimeDate()

        # A combo box to choose what class you're trying to check attendance to
        self.cBoxData = self.ClassSched()
        self.cb = Combobox(window, values=self.cBoxData)
        self.cb.place(x=645, y=100, width=350)

        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(window, text="Check Attendance", command=self.snapshot)
        self.btn_snapshot.pack(side=tk.LEFT)

        # quit button
        self.btn_quit = tk.Button(window, text='QUIT', command=quit)
        self.btn_quit.pack(side=tk.LEFT)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()

        self.window.mainloop()

    def snapshot(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()
        # if ret:
        #     cv2.imwrite("frame-" + time.strftime("%d-%m-%Y-%H-%M-%S") + ".jpg", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))

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
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) #converting frame to grayscale
        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.05, minNeighbors=5) #detecting faces in the frame
        edges = cv2.Canny(gray_frame, 100, 200) #generating edge map using Canny Edge Detector
        for(x,y,w,h) in faces:
            # print(x,y,w,h)
            roi_gray = gray_frame[y:y+h, x:x+w] #cropping the face
            roi_color = frame[y:y+h, x:x+w]
            cv2.rectangle(frame, (x,y), (x+w, y+h), (0,255,0), 2) #drawing rectangle around the face
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
