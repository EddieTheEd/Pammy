import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QListWidget, QDialog, QListWidgetItem, QPushButton  # Ensure QPushButton is imported
)
from PyQt5.QtCore import Qt

class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Task Manager')
        self.setGeometry(100, 100, 600, 400)
        
        self.layout = QVBoxLayout()
        self.tasks_layout = QHBoxLayout()
        
        self.layout.addLayout(self.tasks_layout)
        
        self.setLayout(self.layout)

        self.installEventFilter(self)
        
        self.load_tasks()
    

    def load_tasks(self):
        for i in reversed(range(self.tasks_layout.count())):
            widget = self.tasks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        try:
            with open('tasks.json', 'r') as file:
                content = file.read()
                if content.strip():
                    self.tasks = json.loads(content)
                else:
                    self.tasks = {}

                for group, task_list in self.tasks.items():
                    group_layout = QVBoxLayout()
                    group_label = QLabel(group)
                    group_layout.addWidget(group_label)

                    task_list_widget = QListWidget()
                    task_list_widget.setObjectName(group)
                    task_list_widget.itemPressed.connect(self.on_task_selected)
                    task_list_widget.installEventFilter(self)

                    for task in task_list:
                        task_display = f"{task['taskname']} (Due: {task['duedate']})"
                        item = QListWidgetItem(task_display)
                        item.setData(Qt.UserRole, task)
                        task_list_widget.addItem(item)

                    group_layout.addWidget(task_list_widget)

                    group_container = QWidget()
                    group_container.setLayout(group_layout)

                    self.tasks_layout.addWidget(group_container)
        except FileNotFoundError:
            self.tasks = {}


    def show_add_task_dialog(self):
        dialog = AddTaskDialog(self)
        dialog.exec()

    def add_task(self, task):
        group = task['group']
        if group not in self.tasks:
            self.tasks[group] = []
        
        self.tasks[group].append(task)
        
        with open('tasks.json', 'w') as file:
            json.dump(self.tasks, file, indent=4)
        
        self.load_tasks()

    def on_task_selected(self, item):
        self.selected_task = item
        self.selected_group = item.listWidget().objectName()

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress and event.key() == Qt.Key_Return:
            self.show_add_task_dialog()
            return True
        elif event.type() == event.KeyPress and event.key() == Qt.Key_Delete:
            if hasattr(self, 'selected_task'):
                self.delete_task()
                return True
        return super().eventFilter(obj, event)

    def delete_task(self):
        task = self.selected_task.data(Qt.UserRole)
        group = self.selected_group

        self.tasks[group] = [t for t in self.tasks[group] if t['taskname'] != task['taskname']]

        if not self.tasks[group]:
            del self.tasks[group]

        with open('tasks.json', 'w') as file:
            json.dump(self.tasks, file, indent=4)

        self.load_tasks()

class AddTaskDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Add Task')
        self.setGeometry(150, 150, 300, 200)
        
        self.layout = QVBoxLayout()
        
        self.taskname_input = QLineEdit(self)
        self.taskname_input.setPlaceholderText('Task Name')
        
        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText('Description')
        
        self.group_input = QLineEdit(self)
        self.group_input.setPlaceholderText('Group')
        
        self.set_date_input = QLineEdit(self)
        self.set_date_input.setPlaceholderText('Set Date (YYYY-MM-DD)')
        
        self.due_date_input = QLineEdit(self)
        self.due_date_input.setPlaceholderText('Due Date (YYYY-MM-DD)')
        
        self.submit_button = QPushButton('Add Task')
        self.submit_button.clicked.connect(self.add_task)
        
        self.layout.addWidget(self.taskname_input)
        self.layout.addWidget(self.description_input)
        self.layout.addWidget(self.group_input)
        self.layout.addWidget(self.set_date_input)
        self.layout.addWidget(self.due_date_input)
        self.layout.addWidget(self.submit_button)
        
        self.setLayout(self.layout)

    def add_task(self):
        task = {
            "taskname": self.taskname_input.text(),
            "description": self.description_input.text(),
            "group": self.group_input.text(),
            "setdate": self.set_date_input.text(),
            "duedate": self.due_date_input.text()
        }
        
        if all(task.values()):
            self.parent().add_task(task)
            self.close()
        else:
            QMessageBox.warning(self, 'Input Error', 'Please fill all fields.')

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TaskManager()
    window.show()
    sys.exit(app.exec())