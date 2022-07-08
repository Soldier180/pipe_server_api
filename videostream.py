from threading import Thread
import cv2
import time
import threading
import configparser
import subprocess as sp
import psutil
import subprocess

outputFrame = None
lock = threading.Lock()


class VideoStreamReader:
    def __init__(self, src=0, name="VideoStream", settings_object=None):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.vs = VideoStreamer(settings_object)
        self.vs.start_stream()
        time.sleep(1)
        self.stream = cv2.VideoCapture('udp://127.0.0.1:23000')
        (self.grabbed, self.frame) = self.stream.read()
        self.h, self.w = self.frame.shape[0], self.frame.shape[1]

        # initialize the thread name
        self.name = name

        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

        self.record_stream = False
        self.pause_stream = False
        self.stop_stream = False

        self.record_writer = None

    def start(self):
        # start the thread to read frames from the video stream
        t = Thread(target=self.update, name=self.name, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return

            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            if (self.record_stream == True) and (self.record_writer is None):
                fourcc = cv2.VideoWriter_fourcc(*'MP4V')
                self.record_writer = cv2.VideoWriter('output.mp4', fourcc, 30, (self.w, self.h))

            if (self.record_stream == True) and (not self.pause_stream):
                self.record_writer.write(self.frame)

            if self.stop_stream:
                self.record_stream = False
                self.pause_stream = False
                self.record_writer.release()
                self.stop_stream = False
                self.record_writer = None
                print("stop")


    def read(self):
        # return the frame most recently read
        return self.frame


    def generate(self):
        while True:
            if self.stopped:
                return

            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", self.frame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
            # yield the output frame in the byte format
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.vs.stop_stream()

    def start_record(self, video_path_name):
        self.record_stream = True

    def pause_record(self):
        self.pause_stream = True

    def stop_record(self):
        self.stop_stream = True







class VideoStreamer:
    def __init__(self, setting_object):
        self.setting_object = setting_object
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.cmd = ['ffmpeg',
                    '-loglevel','quiet',
                    '-f', 'dshow',
                #'-re',
                #'-stream_loop',  '-1',
                '-i', 'video=HD Camera',#config["VIDEO"]["file_location"],
               '-preset', 'ultrafast',
                '-vcodec', 'mpeg4',
               '-tune', 'zerolatency',
               '-b', '100k',
               '-f',  'h264',
               self.config["VIDEO"]["stream_address"]]
        # self.cmd = ['ffmpeg', '-re', '-stream_loop', '-1', '-i',
        #             self.config["VIDEO"]["file_location"],
        #             '-preset', 'ultrafast', '-vcodec',
        #             'mpeg4', '-tune', 'zerolatency',
        #             '-b', '900k', '-f', 'h264',
        #             self.config["VIDEO"]["stream_address"]]

    def start_stream(self):
        self.p = subprocess.Popen(self.cmd, shell=True)

    def stop_stream(self):
        process = psutil.Process(self.p.pid)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

# vs = VideoStreamer()
# vs.start_stream()
# import time
# time.sleep(30)
# vs.stop_stream()





# def img_processing():
#     global vs, outputFrame, lock
#     # loop over frames from the video stream
#     while True:
#         frame = vs.read()
#         if not vs.grabbed:
#             continue
#         # lock
#         with lock:
#             outputFrame = frame.copy()
#
#
# def generate():
#     # grab global references to the output frame and lock variables
#     global outputFrame, lock
#     # loop over frames from the output stream
#     while True:
#         # wait until the lock is acquired
#         with lock:
#             # check if the output frame is available, otherwise skip
#             # the iteration of the loop
#             if outputFrame is None:
#                 continue
#             # encode the frame in JPEG format
#             (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
#             # ensure the frame was successfully encoded
#             if not flag:
#                 continue
#         # yield the output frame in the byte format
#         yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
#                bytearray(encodedImage) + b'\r\n')

# vs = VideoStreamReader()
# # count = 0
# vs.start()
# # while count < 10000:
# #     fr = vs.read()
# #     # cv2.waitKey(1)
# #     # cv2.imshow('image', fr)
# #     count+=1
#
# vs.stop()
# cv2.destroyAllWindows()