import json
from datetime import datetime

with open('tasks.json', 'r') as file:
    tasks_data = json.load(file)

tasks = []
for group, task_list in tasks_data.items():
    for task in task_list:
        tasks.append(task)

def sort_by_duedate(task):
    return datetime.strptime(task['duedate'], '%Y-%m-%d %H:%M:%S')

sorted_tasks = sorted(tasks, key=sort_by_duedate)

for task in sorted_tasks:
    print(f"Task Name: {task['taskname']}, Description: {task['description']}, Group: {task['group']}, "
          f"Set Date: {task['setdate']}, Due Date: {task['duedate']}")

