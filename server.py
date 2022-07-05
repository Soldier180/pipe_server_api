import argparse
import configparser
from flask import Flask, request, jsonify
from SettingsObj import SettingsObj
import json
config = configparser.ConfigParser()
config.read('config.ini')


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
        # self.add_url_rule('/video', None, self.get_video_source, methods = ['GET'])
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
                    'inspection_folder': ""},
               'settings': {
                    'video_input': self.setting_obj.settings_dict['settings']['video_input'],
                    'deferred_overlay': self.setting_obj.settings_dict['settings']['deferred_overlay'],
                    'serial_port': self.setting_obj.settings_dict['settings']['serial_port'],
                    'baud_rate': self.setting_obj.settings_dict['settings']['baud_rate'],
                    'truck_type': self.setting_obj.settings_dict['settings']['truck_type'],
                    'show_dist_counter': self.setting_obj.settings_dict['settings']['show_dist_counter'],
                    'distance': self.setting_obj.settings_dict['settings']['distance'],
                    'inspection_folder': self.setting_obj.settings_dict['settings']['inspection_folder']
                }
        }

        return jsonify(res)


    def settings_upd(self):
        print("args :", request.args)
        body = request.get_json()
        print(body)
        for k, v in body['settings'].items():
            if body['settings'][k] != self.setting_obj.settings_dict['settings'][k]:
                #todo set hardware settings
                self.setting_obj.settings_dict['settings'][k] = body['settings'][k]

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

    # def endpoint_chat(self):
    #
    #     print("args :",request.args)
    #     body = request.get_json()
    #     print(body)
    #
    #     res = self.r.process_request(body)
    #     return jsonify(res)


def main():
    host, port = config['WEB_API']['host'], int(config['WEB_API']['port'])
    server = Server(host, 'ai_server')
    print("server run")
    server.run(host=host, port=port, threaded=True)

if __name__ == "__main__":
    main()
