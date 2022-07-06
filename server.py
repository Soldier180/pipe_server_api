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
from videostream import WebcamVideoStream

cmd = ['ffmpeg',
       '-re',
       '-stream_loop', '-1',
       '-i', config["VIDEO"]["file_location"],
       '-preset', 'ultrafast',
       '-vcodec', 'mpeg4',
       '-tune', 'zerolatency',
       '-b', '900k',
       '-f', 'h264',
       config["VIDEO"]["stream_address"]]

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

def start_stream():
    sp.run(cmd)

video_stream_th = threading.Thread(target=start_stream, args=())
# video_stream_th.daemon = True

video_stream_th.start()
import time
time.sleep(3)


outputFrame = None
lock = threading.Lock()

vs = WebcamVideoStream(src=config["VIDEO"]["stream_address"]).start()
time.sleep(1.0)


def img_processing():
    global vs, outputFrame, lock
    # loop over frames from the video stream
    while True:
        frame = vs.read()
        if not vs.grabbed:
            continue
        # lock
        with lock:
            outputFrame = frame.copy()


def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not flag:
                continue
        # yield the output frame in the byte format
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
               bytearray(encodedImage) + b'\r\n')




class Server(Flask):
    def __init__(self, host, name):
        """
        init server class
        """
        super(Server, self).__init__(name)
        self.host = host
        self.define_uri()
        self.setting_obj = SettingsObj()
        #self.r = RequestProcessor()


    def define_uri(self):
        self.provide_automatic_option = False
        self.add_url_rule('/videostream', None, self.video_feed)
        self.add_url_rule('/settings', None, self.get_settings, methods=['GET'])
        self.add_url_rule('/settings', None, self.settings_upd, methods=['PATCH'])
        self.add_url_rule('/test_connection', None, self.test_connection, methods=['GET'])

        # self.add_url_rule('/api', None, self.endpoint_chat, methods=['POST'])

    def version(self,path):
        try:
            return open(path, "r").read()
        except FileNotFoundError as _err:
            return 'undefined'


    def test_connection(self):
        return jsonify({"status" : True})

    def get_video_source(self):
        res = {'video_link':"udp:localhost:12345"
        }
        return jsonify(res)

    def get_settings(self):
        res = {'variants': {
                    'video_input': ["Hauppauge Cx23100 Video Capture", "source2"],
                    'deferred_overlay': [True, False],
                    'serial_port': ["COM1", "COM2"],
                    'baud_rate': [150, 300, 600, 1200, 1800, 2400, 4800, 7200, 9600, 14400, 19200, 38400, 57600],
                    'truck_type': ["type1", "type2", "type3"],
                    'show_dist_counter': [True, False],
                    'distance': ['ft', 'm'],
                    'inspection_folder': "",
                    'clicks_per_foot' : ""},
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

        # {'video_settings': {'video_input': ["s1", "s2"],
        #                     'deferred_overlay': True},
        #        'serial_port_settings': {'serial_port': ["COM3_1", "COM3_2"],
        #                                 'baud_rate': [150, 300, 600, 1200, 1800, 2400, 4800, 7200, 9600, 14400, 19200, 38400, 57600],
        #                                 'truck_type':["type1", "type2", "type3"],
        #                                 'clicks_per_foot':1000,
        #                                 'show_dist_counter': True,
        #                                 'distance' : ['ft', 'm']},
        #        'inspection_folder': ""
        #
        #
        # }
        return "ok"

    def video_feed(self):
        return Response(generate(),
                        mimetype="multipart/x-mixed-replace; boundary=frame")



    # def endpoint_chat(self):
    #
    #     print("args :",request.args)
    #     body = request.get_json()
    #     print(body)
    #
    #     res = self.r.process_request(body)
    #     return jsonify(res)


def main():
    t = threading.Thread(target=img_processing, args=())
    t.daemon = True
    t.start()
    host, port = config['WEB_API']['host'], int(config['WEB_API']['port'])
    server = Server(host, 'ai_server')
    cors = CORS(server)
    server.config['CORS_HEADERS'] = 'Content-Type'

    # CORS(server)
    print("server run")
    server.run(host=host, port=port, threaded=True)

if __name__ == "__main__":
    main()
