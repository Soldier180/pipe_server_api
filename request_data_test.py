import configparser
import json
config = configparser.ConfigParser()
config.read('config.ini')
import requests
from requests.structures import CaseInsensitiveDict
host, port = config['WEB_API']['host'], int(config['WEB_API']['port'])
url = "http://"+ host +":" + str(port)

###GET connection_test
print("-GET- TEST CONNECTION")
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
resp = requests.get(url + "/test_connection", headers=headers)
print(resp.content)
print(resp.status_code)


###GET settings
print("-GET- SETTINGS")
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
resp = requests.get(url + "/settings", headers=headers)
print(resp.content)
print(resp.status_code)

###PATCH settings
print("-PATCH- SETTINGS")
headers = CaseInsensitiveDict()
headers["Accept"] = "application/json"
headers["Content-Type"] = "application/json"

data = {"variants": {
                    "video_input": ["Hauppauge Cx23100 Video Capture", "source2"],
                    "deferred_overlay": [True, False],
                    "serial_port": ["COM1", "COM2"],
                    "baud_rate": [150, 300, 600, 1200, 1800, 2400, 4800, 7200, 9600, 14400, 19200, 38400, 57600],
                    "truck_type": ["type1", "type2", "type3"],
                    "show_dist_counter": [True, False],
                    "distance": ["ft", "m"],
                    "inspection_folder": ""},
               "settings": {"video_input": "",
                    "deferred_overlay": True,
                    "serial_port": "",
                    "baud_rate": 9600,
                    "truck_type": "",
                    "show_dist_counter": False,
                    "distance": "",
                    "inspection_folder": ""}
        }


from flask import jsonify
import json
data2 = json.dumps(data).encode('utf-8')
resp = requests.patch(url + "/settings", headers=headers, data=data2)
print(resp.content)
print(resp.status_code)