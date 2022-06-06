###
# Final Project for Graphics and Visual Computing Course
###

## The main program
from datetime import datetime, datetime, timedelta
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
import csv
from Detector import Detector
import numpy as np
import time

api = web_api.API()
CamScaleW = 645
CamScaleH = 810
csvData = [{'x': 0, 'y': 0, 'w': 0, 'h': 0}]


def get_rect_min():
    min = [999, 999, 999, 999]
    with open('rectAvg.csv', 'r') as f:
        reader = csv.reader(f, skipinitialspace=True, delimiter=',')
        next(reader, None)  # skip the headers
        next(reader, None)  # skip the init values
        for row in reader:
            # print(row)
            if (int(row[0]) < min[0]) and \
                    (int(row[1]) < min[1]) and \
                    (int(row[2]) < min[2]) and \
                    (int(row[3]) < min[3]):
                min = [int(row[0]), int(row[1]), int(row[2]), int(row[3])]

    print(min)
    return min


def get_rect_max():
    max = [0, 0, 0, 0]
    with open('rectAvg.csv', 'r') as f:
        reader = csv.reader(f, skipinitialspace=True, delimiter=',')
        next(reader, None)  # skip the headers
        for row in reader:
            if (int(row[0]) > max[0]) and \
                    (int(row[1]) > max[1]) and \
                    (int(row[2]) > max[2]) and \
                    (int(row[3]) > max[3]):
                max = [int(row[0]), int(row[1]), int(row[2]), int(row[3])]

    return max


rect_min = get_rect_min()
rect_max = get_rect_max()


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
        self.window.geometry(str(CamScaleW) + "x" + str(CamScaleH) + "+300+100")
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
        self.id_label.grid(row=2, column=0, columnspan=2, sticky='S')
        self.cBoxData = self.ClassSched()
        self.cb = Combobox(window, values=self.cBoxData, state='readonly')
        self.cb.grid(row=3, column=0, columnspan=2, ipadx=100, ipady=5, pady=15)

        # employee ID input
        self.id_label = tk.Label(window, text='Faculty ID', font=('Montserrat', 12, 'bold'))
        self.id_label.grid(row=4, column=0, columnspan=2, sticky='S')
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
            inputID = self.eID.get()
            print(inputID)
            # get the time with 12hr format HH:MM AM/PM
            _time = time.strftime("%I:%M %p")
            print("Time: ")
            print(_time)
            # get the class schedule from cbox
            sched_index = self.cb.current()
            sbc.set_brightness(curr_brightness)
            flash.ww.destroy()
            print("ddd")
            print(api.check_if_account_exists(inputID))  # test
            if api.check_if_account_exists(inputID):
                print("ID exists!")
                remark = remarks(sched_index)
                addAttendance(remark, sched_index, inputID)

            else:
                print("ID doesn't exist!")
                return

        # Created by Bohol, Christopher
        # Modification by: Montero, Joshua
        def remarks(index):
            # get the index of sch_time in class_schedule
            selectedCode = self.codes[index]
            # split the sch_time by spaces
            sch_time = selectedCode['sch_time'].split(' - ')

            start = sch_time[0]
            print(start)
            end = sch_time[1]
            print(end)

            # convert the start and end time to 24hr format
            start = time.strptime(start, "%I:%M %p")
            start = time.strftime("%H:%M", start)
            print(start)

            end = time.strptime(end, "%I:%M %p")
            end = time.strftime("%H:%M", end)
            print(end)

            _time = time.strftime("%H:%M")
            # print(_time)
            
            # split the start and end time by :
            startS = start.split(':')
            # print(startS)

            endS = end.split(':')
            # print(endS)

            # split the time by :
            timeX = _time.split(':')
            # print(timeX)

            # convert the start and end time to int
            startInts = [int(i) for i in startS]
            print(startInts)

            endInts = [int(i) for i in endS]
            print(endInts)

            # convert the time to int
            timeS = [int(i) for i in timeX]
            print(timeS)

            add = startInts[1] + 15  # 15 minutes late
            print(add)


            if (timeS[0] > startInts[0]) and (timeS[1] >= endInts[1]):
                remark = "Absent"
                print(remark)
                return remark
            if timeS[0] < startInts[0]:
                remark = "Early"
                print(remark)
                return remark
            if timeS[0] == startInts[0]:
                if (timeS[1] >= startInts[1]) and (timeS[1] <= add):
                    remark = "Present"
                    print(remark)
                    return remark
                elif timeS[1] >= add:
                    remark = "Late"
                    print(remark)
                    return remark
            else:
                remark = "Absent"
                print(remark)
                return remark

        def addAttendance(remark, index, id):
            selectedCode = self.codes[index]
            data = {
                'remarks': remark,
                'classcode': int(selectedCode['offer_no']),
                'date': strftime('%d/%m/%Y'),
                'time': strftime('%I:%M %p'),
                'employeeID': int(id)
            }
            print(data)
            response = api.add_attendance(body=data)
            print(response.json())
            # try:
            #     if response['success']:
            #         print("adding attendance success!!")
            # except:
            #     print("adding attendance failed")
            #     print("API Error!")

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
        time_string = strftime('%I:%M:%S %p\n%A, %x')  # time format
        self.timeDate.config(text=time_string)
        self.timeDate.after(1000, self.TimeDate)  # time delay of 1000 milliseconds

    # Modified by Bohol, Cristopher
    def ClassSched(self):
        # get the class schedule from api
        self.class_schedule = api.get_all_schedule()
        # print(self.class_schedule)
        self.codes = self.class_schedule['data']
        # print(self.codes)
        # display the offer_no in class_schedule
        self.cBoxDataList = list()
        for i in self.codes:
            self.cBoxDataList.append(i['offer_no'] + ' - ' +
            i['subj_no'] + ' | ( ' +
            i['sch_time'] + ' ) | ' +
            i['subj_name']
            )
        return tuple(self.cBoxDataList)


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.source = video_source
        self.obj_detector = Detector(videopath=self.source)
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

    # To get frames
    def get_frame(self):
        if self.vid.isOpened():

            ret, fr = self.vid.read()
            if ret:
                self.edge_detection(frame=fr)
                self.obj_detection(frame=fr)
                # self.rectAvg_to_csv(data=csvData)  # Enable only if you want to get the average again

                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(fr, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (None, None)

    def rectAvg_to_csv(self, data):
        header = ['x', 'y', 'w', 'h']
        # open the file in the write mode
        with open('rectAvg.csv', 'w+', newline='') as f:
            # create the csv writer
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            writer.writerows(data)

    # added by Montero, Joshua & Gadianne, James & Bohol, Christopher
    def obj_detection(self, frame):
        classLabelIDs, confidence, bboxes = self.obj_detector.net.detect(frame, confThreshold=0.4)
        bboxes = list(bboxes)
        confidence = list(np.array(confidence).reshape(1, -1)[0])
        confidence = list(map(float, confidence))

        bboxIdx = cv2.dnn.NMSBoxes(bboxes, confidence, score_threshold=0.5, nms_threshold=0.2)

        if len(bboxIdx) != 0:
            for i in range(0, len(bboxIdx)):
                bbox = bboxes[np.squeeze(bboxIdx[i])]
                classConfidence = confidence[np.squeeze(bboxIdx[i])]
                classLabelID = np.squeeze(classLabelIDs[[np.squeeze(bboxIdx[i])]])
                classesLabel = self.obj_detector.classesList[classLabelID]
                classColor = [int(c) for c in self.obj_detector.colorList[classLabelID]]

                objText = "{}:{:.4f}".format(classesLabel, classConfidence)

                x, y, w, h = bbox
                cv2.rectangle(frame, (x, y), (x + w, y + h), color=classColor, thickness=2)
                cv2.putText(frame, objText, (x, y - 10), cv2.FONT_HERSHEY_PLAIN, 1, classColor, 2)

    # added by Bohol, Christopher
    def edge_detection(self, frame):

        def appendRect(_x, _y, _w, _h):
            csvData.append({'x': _x, 'y': _y, 'w': _w, 'h': _h})

        path = "cascades\\data\\haarcascade_frontalface_alt_tree.xml"
        face_cascade = cv2.CascadeClassifier(path)

        # added and edited by Gadiane, James Christian
        # modified by Montero, Joshua - Color Spaces discrimination
        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read("trained.yml")
        with open("labels.pkl", 'rb') as f:
            main_labels = pickle.load(f)
            labels = {v: k for k, v in main_labels.items()}

        HSV_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2HSV)
        YCbCr_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2YCrCb)
        LUV_cv = cv2.cvtColor(frame, cv2.COLOR_RGB2LUV)

        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)  # converting frame to grayscale
        HSV_cv = cv2.cvtColor(HSV_cv, cv2.COLOR_BGR2GRAY)
        YCbCr_cv = cv2.cvtColor(YCbCr_cv, cv2.COLOR_BGR2GRAY)
        LUV_cv = cv2.cvtColor(LUV_cv, cv2.COLOR_BGR2GRAY)

        faces = face_cascade.detectMultiScale(gray_frame, scaleFactor=1.1,
                                              minNeighbors=5)  # detecting faces in the frame
        # edges = cv2.Canny(gray_frame, 100, 200) #generating edge map using Canny Edge Detector

        font = cv2.FONT_HERSHEY_SIMPLEX
        fScale = (CamScaleW * CamScaleH) / (900 * 900)
        stroke = 2
        for (x, y, w, h) in faces:
            point = (x, y)
            print(x, y, w, h)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), stroke)
            # roi_gray = gray_frame[y:y+h, x:x+w] #cropping the face
            HSV_frame = HSV_cv[y:y + h, x:x + w]
            YCbCr_frame = YCbCr_cv[y:y + h, x:x + w]
            # LUV_frame = LUV_cv[y:y+h, x:x+w]

            # id_1, conf1 = recognizer.predict(roi_gray)
            id_2, conf2 = recognizer.predict(HSV_frame)
            id_3, conf3 = recognizer.predict(YCbCr_frame)
            # id_4, conf4 = recognizer.predict(LUV_frame)

            if not (rect_min[0] < x and rect_min[1] < y and rect_min[2] < w and rect_min[3] < h) and \
                   not (rect_max[0] > x and rect_max[1] > y and rect_max[2] > w and rect_max[3] > h):

                # if conf4 >= 65 and conf4 <= 70:
                #     print("LUV!!")
                #     # print(labels[id_])
                #     # appendRect(x,y,w,h)
                #     self.name = labels[id_4]
                #     color = (255, 255, 255)
                #     cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
                #     continue

                if conf2 >= 50 and conf2 <= 80:
                    print("HSV!!")
                    # appendRect(x, y, w, h)
                    self.name = labels[id_2]
                    color = (255, 255, 255)
                    cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
                    continue
                if conf3 >= 65 and conf3 <= 80:
                    print("YCbCr!!")
                    # appendRect(x, y, w, h)
                    self.name = "False"
                    color = (0, 0, 255)
                    cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
                    cv2.rectangle(frame, point, (x + w, y + h), color, stroke)
                    # continue
                # if conf1 >= 75 and conf1 <= 80:
                #     print("grayscale!!!!")
                #     # appendRect(x,y,w,h)
                #     self.name = labels[id_1]
                #     color = (255, 255, 255)
                #     cv2.putText(frame, self.name, point, font, fScale, color, stroke, cv2.LINE_AA)
                else:
                    name = "False"
                    color = (0, 0, 255)
                    cv2.putText(frame, name, point, font, fScale, color, stroke, cv2.LINE_AA)
                    cv2.rectangle(frame, point, (x + w, y + h), color, stroke)
                # drawing rectangle around the face
            else:
                name = "Position face properly..."
                color = (255, 0, 255)
                cv2.putText(frame, name, point, font, fScale, color, stroke, cv2.LINE_AA)
                cv2.rectangle(frame, point, (x + w, y + h), color, stroke)

            # cv2.imshow('gray', roi_gray)
            cv2.imshow('HSV', HSV_frame)
            cv2.imshow('YCC', YCbCr_frame)
            # cv2.imshow('LUV', LUV_frame)
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
