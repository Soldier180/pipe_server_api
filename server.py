import argparse
import configparser
from flask import Flask, request, jsonify
from SettingsObj import SettingsObj
import json
from flask import Response
from flask_cors import CORS
import threading
import cv2
config = configparser.ConfigParser()
config.read('config.ini')
# config stream
import subprocess as sp
from videostream import VideoStreamReader

# cmd = ['ffmpeg',
#         '-f', 'dshow',#'-re',
#         #'-stream_loop',  '-1',
#         '-i', 'video=HD Camera',#config["VIDEO"]["file_location"],
#        '-preset', 'ultrafast',
#         '-vcodec', 'mpeg4',
#        '-tune', 'zerolatency',
#        '-b', '100k',
#        '-f',  'h264',
#        config["VIDEO"]["stream_address"]]

# def start_stream():
#     sp.run(cmd)
#
# video_stream_th = threading.Thread(target=start_stream, args=())
# # video_stream_th.daemon = True
#
# video_stream_th.start()
# import time
# time.sleep(3)
#
#
# outputFrame = None
# lock = threading.Lock()
#
# vs = VideoStreamReader(src=config["VIDEO"]["stream_address"]).start()
# time.sleep(1.0)
#
#
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




class Server(Flask):
    def __init__(self, host, name):
        """
        init server class
        """
        super(Server, self).__init__(name)
        self.host = host
        self.define_uri()
        self.setting_obj = SettingsObj()
        self.stream = False
        self.stream_object = None
        #self.r = RequestProcessor()


    def define_uri(self):
        self.provide_automatic_option = False
        self.add_url_rule('/videostream', None, self.video_feed)
        self.add_url_rule('/videostream/status', None, self.record_pause_stop, methods=['GET'])
        self.add_url_rule('/settings', None, self.get_settings, methods=['GET'])
        self.add_url_rule('/settings', None, self.settings_upd, methods=['PATCH'])
        self.add_url_rule('/test_connection', None, self.test_connection, methods=['GET'])

    def record_pause_stop(self):
        print("args :", request.args)
        body = request.get_json()
        print(body)
        if (body['status'] == 'started') and (self.stream == False):
            self.start_stream(body['video_id'])
            return Response("Started stream", status=200)
        elif (body['status'] == 'started') and (self.stream == True):
            self.start_record()
            return Response("Started record", status=200)
        elif body['status'] == 'paused':
            self.pause_record()
            return Response("Paused record", status=200)
        elif body['status'] == 'stopped':
            self.stop_record()
            return Response("Stopped record", status=200)

        return Response("Error", status=400)

    def start_stream(self, video_id):
        #todo create dirs

        self.stream = True
        if self.stream_object is None:
            self.stream_object = VideoStreamReader()
            self.stream_object.start()

    def start_record(self):
        if self.stream_object is not None:
            self.stream_object.start_record("fgh")

    def pause_record(self):
        if self.stream_object is not None:
            self.stream_object.pause_record()

    def stop_record(self):
        if self.stream_object is not None:
            self.stream_object.stop_record()


    def test_connection(self):
        return jsonify({"status" : True})

    def get_video_source(self):
        res = {'video_link':"udp:localhost:12345"
        }
        return jsonify(res)

    def get_settings(self):
        res = {'variants': {
                    'video_input': [self.setting_obj.settings_dict['settings']['video_input']],
                    'deferred_overlay': [True, False],
                    'serial_port': ["COM1"],
                    'baud_rate': [150, 300, 600, 1200, 1800, 2400, 4800, 7200, 9600, 14400, 19200, 38400, 57600],
                    'truck_type': ["type1", "type2", "type3"],
                    'show_dist_counter': [True, False],
                    'distance': ['ft', 'm'],
                    'inspection_folder': "",
                    'clicks_per_foot': ""},
               'settings': {
                    'video_input': self.setting_obj.settings_dict['settings']['video_input'],
                    'deferred_overlay': self.setting_obj.settings_dict['settings']['deferred_overlay'],
                    'serial_port': self.setting_obj.settings_dict['settings']['serial_port'],
                    'baud_rate': self.setting_obj.settings_dict['settings']['baud_rate'],
                    'truck_type': self.setting_obj.settings_dict['settings']['truck_type'],
                    'show_dist_counter': self.setting_obj.settings_dict['settings']['show_dist_counter'],
                    'distance': self.setting_obj.settings_dict['settings']['distance'],
                    'inspection_folder': self.setting_obj.settings_dict['settings']['inspection_folder'],
                    'clicks_per_foot': self.setting_obj.settings_dict['settings']['clicks_per_foot'],
                }
        }

        return jsonify(res)


    def settings_upd(self):
        print("args :", request.args)
        body = request.get_json()
        print(body)
        for k, v in body.items():
            if body[k] != self.setting_obj.settings_dict['settings'][k]:
                #todo set hardware settings
                self.setting_obj.settings_dict['settings'][k] = body[k]
        return "ok"

    def video_feed(self):
        while self.stream_object is not None:
            return Response(self.stream_object.generate(),
                            mimetype="multipart/x-mixed-replace; boundary=frame")




def main():
    host, port = config['WEB_API']['host'], int(config['WEB_API']['port'])
    server = Server(host, 'ai_server')
    cors = CORS(server)
    server.config['CORS_HEADERS'] = 'Content-Type'

    # CORS(server)
    print("server run")
    server.run(host=host, port=port, threaded=True)

if __name__ == "__main__":
    main()
