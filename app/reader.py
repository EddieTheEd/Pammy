import json
from datetime import datetime
import subprocess
from gi.repository import GObject
from gi.repository import Notify

with open('tasks.json', 'r') as file:
    tasks_data = json.load(file)

tasks = []
for group, task_list in tasks_data.items():
    for task in task_list:
        tasks.append(task)

def sort_by_duedate(task):
    return datetime.strptime(task['duedate'], '%Y-%m-%d %H:%M:%S')

sorted_tasks = sorted(tasks, key=sort_by_duedate)

class Notifier(GObject.Object):
    def __init__(self):

        super(Notifier, self).__init__()
        Notify.init("Pammy")

    def send_notification(self, title, text, file_path_to_icon="/home/edwardhuynh/Projects/Pammy/pammy.png"):

        print(text)
        n = Notify.Notification.new(title, "<i>hi</i>", file_path_to_icon)
        n.show()

App = Notifier()

for task in sorted_tasks:
    App.send_notification(task['taskname'], str(task['description']) + " - " + datetime.strptime(task['duedate'], '%Y-%m-%d %H:%M:%S').strftime('%m/%d/%Y %I:%M %p'))




