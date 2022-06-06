import requests
import os
from dotenv import load_dotenv

load_dotenv()

class API():
    def __init__(self):
        #  self.url = str(os.getenv('LOCAL_API'))  # Local URL
        self.url = "http://localhost:5000/facial-recognition-syste-c82ae/us-central1"  # Local URL

    def get_account(self, id):
        return requests.get(url=self.url + "/api/accounts/get/" + str(id))


    # If ID/Account doesn't exist
    # {
    # 	"success": false,
    # 	"data": "This ID does not exist"
    # }#

    def add_attendance(self, body):
        return requests.post(url=self.url + "user/addAttendance", json=body)

    def check_if_account_exists(self, id):
        response = self.get_account(str(id))
        # print(response)
        data = response.json()
        # print(type(data))
        # print(data)
        try:
            if data['success']:
                return True
            else:
                return False
        except:
            return False

    def get_all_schedule(self):
        response = requests.get(url=self.url + "/api/schedule/get/all")
        data = response.json()
        return data
