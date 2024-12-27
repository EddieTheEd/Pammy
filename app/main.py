import json
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QListWidget, QDialog, QListWidgetItem, QPushButton, QDateTimeEdit,
    QDesktopWidget, QCheckBox, QSizePolicy
)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon


class TaskManager(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Pammy')
        self.setGeometry(100, 100, 600, 400)
        
        self.layout = QVBoxLayout()
        self.tasks_layout = QHBoxLayout()
        
        self.no_tasks_label = QLabel("No tasks yet.<br>Make one by pressing Enter.")
        self.no_tasks_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.no_tasks_label)
        self.layout.addLayout(self.tasks_layout)
        
        self.setLayout(self.layout)

        self.installEventFilter(self)

        self.setWindowIcon(QIcon('pammy.ico'))

        self.showMaximized()
        
        self.load_tasks()

    def eventFilter(self, obj, event):
        if isinstance(obj, QListWidget) and event.type() == event.KeyPress:
            if event.key() == Qt.Key_Return:
                self.show_add_task_dialog()
                return True
            elif event.key() == Qt.Key_Delete:
                if hasattr(self, 'selected_task'):
                    self.delete_task()
                    return True
            elif event.key() == Qt.Key_W and event.modifiers() == Qt.ControlModifier:
                self.close()
                return True
        return super().eventFilter(obj, event)

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

                if not self.tasks:
                    self.no_tasks_label.show()
                else:
                    self.no_tasks_label.hide()

                for group, task_list in self.tasks.items():
                    group_layout = QVBoxLayout()
                    group_label = QLabel(group)
                    group_layout.addWidget(group_label)

                    task_list_widget = QListWidget()
                    task_list_widget.setObjectName(group)
                    task_list_widget.selectionModel().selectionChanged.connect(self.on_task_selected)
                    self.selected_task_list_widget = task_list_widget
                    task_list_widget.installEventFilter(self)

                    for task in task_list:
                        task_display = f"{task['taskname']}: {task['description']} (Due: {task['duedate']}) (Set: {task['setdate']})"
                        item = QListWidgetItem()
                        item.setText(task_display)
                        item.setData(Qt.UserRole, task)
                        task_list_widget.addItem(item)

                    group_layout.addWidget(task_list_widget)

                    group_container = QWidget()
                    group_container.setLayout(group_layout)

                    self.tasks_layout.addWidget(group_container)
        except FileNotFoundError:
            self.tasks = {}
            self.no_tasks_label.show()

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

    def on_task_selected(self, selected):
        selected_index = selected.indexes()[0] if selected.indexes() else None
        if selected_index:
            self.selected_task = self.selected_task_list_widget.itemFromIndex(selected_index)
            self.selected_group = self.selected_task_list_widget.objectName()

    def delete_task(self):
        task = self.selected_task.data(Qt.UserRole)
        group = self.selected_group

        self.load_tasks()
        
        self.tasks[group].remove(task)

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

        self.center_on_screen()
        
        self.taskname_input = QLineEdit(self)
        self.taskname_input.setPlaceholderText('Task Name')
        
        self.description_input = QLineEdit(self)
        self.description_input.setPlaceholderText('Description')
        
        self.group_input = QLineEdit(self)
        self.group_input.setPlaceholderText('Group')
        
        self.set_date_input = QDateTimeEdit(self)
        self.set_date_input.setDateTime(QDateTime.currentDateTime())
        self.set_date_input.hide()

        self.due_date = QCheckBox('Due Date? (Press Space)')

        self.due_date_label = QLabel('Due Date:')
        self.due_date_label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        self.due_date_input = QDateTimeEdit(self)
        
        self.submit_button = QPushButton('Add Task')
        self.submit_button.clicked.connect(self.add_task)

        self.due_date_layout = QHBoxLayout()
        self.due_date_layout.addWidget(self.due_date_label)
        self.due_date_layout.addWidget(self.due_date_input)

        self.layout.addWidget(self.taskname_input)
        self.layout.addWidget(self.description_input)
        self.layout.addWidget(self.group_input)
        self.layout.addWidget(self.set_date_input)
        self.layout.addWidget(self.due_date)
        self.layout.addLayout(self.due_date_layout)
        self.layout.addWidget(self.submit_button)

        self.due_date.setFocusPolicy(Qt.TabFocus)
        
        self.setLayout(self.layout)

        self.setWindowIcon(QIcon('pammy.ico'))

        self.setTabOrder(self.taskname_input, self.description_input)
        self.setTabOrder(self.description_input, self.group_input)
        self.setTabOrder(self.group_input, self.due_date)
        self.setTabOrder(self.due_date, self.due_date_input)
        self.setTabOrder(self.due_date_input, self.submit_button)

    def center_on_screen(self):
        screen = QDesktopWidget().availableGeometry().center()
        frame_geometry = self.frameGeometry()
        frame_geometry.moveCenter(screen)
        self.move(frame_geometry.topLeft())

    def add_task(self):
        if self.due_date.isChecked():
            task = {
                "taskname": self.taskname_input.text(),
                "description": self.description_input.text(),
                "group": self.group_input.text(),
                "setdate": self.set_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                "duedate": 'N/A'
            }
        else:
            task = {
                "taskname": self.taskname_input.text(),
                "description": self.description_input.text(),
                "group": self.group_input.text(),
                "setdate": self.set_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
                "duedate": self.due_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss") 
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
