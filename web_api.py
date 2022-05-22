import requests
import os
from dotenv import load_dotenv

load_dotenv()

class API():
    def __init__(self):
        # self.url = str(os.getenv('DEPLOYED_API'))  # Deployed URL
        self.url = str(os.getenv('LOCAL_API') )  # Local URL

    def get_account(self, id):
        return requests.get(url=self.url + "user/getAccount/" + str(id))

    # If ID/Account doesn't exist
    # {
    # 	"success": false,
    # 	"data": "This ID does not exist"
    # }#

    def add_attendance(self, body):
        return requests.post(url=self.url + "user/addAttendance", json=body)

    def check_if_account_exists(self, id):
        response = self.get_account(str(id))
        data = response.json()
        print(type(data))
        print(data)
        try:
            return data['id'] == id
        except:
            return False
