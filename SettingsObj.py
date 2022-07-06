import os
import pickle
class SettingsObj:
    def __init__(self):
        # todo read from db
        self.settings_dict = {'settings': {'video_input': "",
            'deferred_overlay': False,
            'serial_port': "",
            'baud_rate': 0,
            'truck_type': "",
            'show_dist_counter': False,
            'distance': "",
            'inspection_folder': "",
            'clicks_per_foot' : ""}}


    # {'video_settings': {'video_input': ["Hauppauge Cx23100 Video Capture", "source2"],
    #                     'deferred_overlay': True},
    #  'serial_port_settings': {'serial_port': ["COM1", "COM2"],
    #                           'baud_rate': [150, 300, 600, 1200, 1800, 2400, 4800, 7200, 9600, 14400, 19200, 38400,
    #                                         57600],
    #                           'truck_type': ["type1", "type2", "type3"],
    #                           'clicks_per_foot': 1000,
    #                           'show_dist_counter': True,
    #                           'distance': ['ft', 'm']},
    #  'inspection_folder': ""
    #  }