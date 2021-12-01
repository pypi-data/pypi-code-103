import os, sys
import requests
from . import zaco
from . import func
from . import remote

# UPSTREAM_URL = "http://0.0.0.0:9008"
UPSTREAM_URL = "http://10.40.34.19:9008"

class ProjectTaskClass:

    def __init__(self, id, name, description, color):
        self.id = id
        self.name = name
        self.description = description
        self.color = color

class ProjectRef:

    def __init__(self, ref_id):
        self.ref_id = ref_id
        self.version_id, self.task_id = [int(a) for a in ref_id.split("_")]
        self.classes = []
        self.task_ref = None
        self.parse_raw_func = None

    def load(self):
        # Request task info json
        data = requests.post(f"{UPSTREAM_URL}/ref/{self.version_id}/{self.task_id}", json={'client':func.get_ssh_info().to_dict()})
        loaded_raw_task = None
        if data.status_code == 200:
            data_js = data.json()
            if data_js['success']:
                loaded_raw_task = data_js['result']
            else:
                raise Exception(data.text)
        else:
            raise Exception(data.text)

        # Load to ZACO
        task = zaco.LabelTask(loaded_raw_task)
        self._task = task

        data_type = self._task.label_task_data['info']['data_type'] 
        if data_type == 'Image':
            self.parse_raw_func = remote.get_img_file
        elif data_type == 'Voice':
            self.parse_raw_func = remote.get_numpy_file
        elif data_type == 'Text':
            self.parse_raw_func = remote.get_text_file
        elif data_type == 'Videos':
            self.parse_raw_func = remote.get_file_io

        for c_id, c in self._task.classes.items():
            print(c)
            self.classes.append(ProjectTaskClass(c['id'], 
            c['name'], 
            c['description'],
            c['color']))

    def get_item_ids(self, class_ids=[], rating=-1):
        return self._task.get_item_ids([], class_ids=class_ids, rating=rating)

    def get_items(self, item_ids):
        return self._task.get_items(item_ids)

    def load_item_raw(self, item):
        db_id = item['dataset_id']
        item_fname = item['path']['server_path']
        url = f"{UPSTREAM_URL}/file/{self.version_id}/{self.task_id}/{db_id}/{item_fname}"
        return self.parse_raw_func(url)

# {
#    "success":true,
#    "result":{
#       "info":{
#          "id":595,
#          "name":"Filter more class",
#          "description":"Filter more class des",
#          "task_type":"Classification",
#          "data_type":"Image",
#          "export_date":"2021-07-22-13-59-29"
#       },
#       "data_items":[
#          {
#             "id":"1173_7",
#             "dataset_id":1173,
#             "info":{
#                "url":"https://supplier.lab.zalo.ai/routing/863f6579eb5741a9b8780b39c711b2ee/100575_Name_01.jpg"
#             },
#             "server_path":"9op7ihcg66ag1pzq31n3m8lf9s638e936la69e0ez3yk2vrw92.jpg"
#          },
#          {
#             "id":"1173_5",
#             "dataset_id":1173,
#             "info":{
#                "url":"https://supplier.lab.zalo.ai/routing/863f6579eb5741a9b8780b39c711b2ee/100225_Name_01.jpg"
#             },
#             "server_path":"38j65x7r71pwn8x9e0t846nn7ue07tm470x0oy9m5fpqyt9l3w.jpg"
#          }
#       ],
#       "annotations":[
#          {
#             "id":3,
#             "data_item_id":"1173_7",
#             "class_id":1251,
#             "content":{
               
#             },
#             "user_id":40,
#             "time_stamp":"2021-07-16-15-23-37",
#             "session_id":37122,
#             "review":{
#                "rating":0,
#                "message":"",
#                "time_stamp":""
#             }
#          },
#          {
#             "id":4,
#             "data_item_id":"1173_5",
#             "class_id":1252,
#             "content":{
               
#             },
#             "user_id":40,
#             "time_stamp":"2021-07-16-15-23-37",
#             "session_id":37122,
#             "review":{
#                "rating":0,
#                "message":"",
#                "time_stamp":""
#             }
#          }
#       ],
#       "datasets":[
#          {
#             "id":1173,
#             "name":"Test Flow",
#             "base_path":"a3eb2136be0b44488b586df7d9aefc4b",
#             "data_category_id":1,
#             "description":"Test description",
#             "data_num":2
#          }
#       ],
#       "classes":[
#          {
#             "id":1250,
#             "name":"Other",
#             "color":"#474747",
#             "description":"Other"
#          },
#          {
#             "id":1251,
#             "name":"Class 1",
#             "color":"#FF1FB2",
#             "description":""
#          },
#          {
#             "id":1252,
#             "name":"Class 2",
#             "color":"#12A6FF",
#             "description":""
#          }
#       ],
#       "inputs":[
         
#       ],
#       "task_member":[
#          {
#             "id":14085,
#             "user_id":40,
#             "role_id":1,
#             "creator_id":40,
#             "create_timestamp":"2021-07-16 15:23:22",
#             "mod_timestamp":"2021-07-16 15:23:22",
#             "user_name":"Duy Đàm",
#             "creator_name":"Duy Đàm",
#             "role_name":"Owner",
#             "role_level":3,
#             "user_picture":"https://avatar.talk.zdn.vn/e/2/8/a/34/75/802528ed20a1f3cef0b80b401f69eb19.jpg",
#             "creator_picture":"https://avatar.talk.zdn.vn/e/2/8/a/34/75/802528ed20a1f3cef0b80b401f69eb19.jpg",
#             "active_for_project":1,
#             "team_id":0,
#             "supervise":[
               
#             ]
#          }
#       ],
#       "project_member":[
#          {
#             "id":5,
#             "project_id":11,
#             "role_id":2,
#             "user_id":40,
#             "creator_id":40,
#             "create_timestamp":"2021-07-22-13-59-24",
#             "mod_timestamp":"2021-07-22-13-59-24",
#             "active":1
#          }
#       ]
#    }
# }