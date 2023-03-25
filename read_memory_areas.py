import sys
import snap7
from snap7.util import *
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QMessageBox

IP_ADDRESS = "192.168.0.1"
RACK = 0
SLOT = 1

tags = []

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("PLC Tag Viewer")
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        self.tag_input_layout = QHBoxLayout()
        self.layout.addLayout(self.tag_input_layout)

        self.name_label = QLabel("Name:")
        self.tag_input_layout.addWidget(self.name_label)

        self.name_input = QLineEdit()
        self.tag_input_layout.addWidget(self.name_input)

        self.type_label = QLabel("Type:")
        self.tag_input_layout.addWidget(self.type_label)

        self.type_input = QLineEdit()
        self.tag_input_layout.addWidget(self.type_input)

        self.add_button = QPushButton("Add Tag")
        self.tag_input_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_tag)

        self.remove_button = QPushButton("Remove Tag")
        self.tag_input_layout.addWidget(self.remove_button)
        self.remove_button.clicked.connect(self.remove_tag)

        self.tag_table = QTableWidget()
        self.layout.addWidget(self.tag_table)
        self.tag_table.setColumnCount(3)
        self.tag_table.setHorizontalHeaderLabels(["Name", "Type", "Value"])
        self.tag_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_tags)
        self.timer.start(1000)

    def add_tag(self):
        name = self.name_input.text()
        tag_type = self.type_input.text()
        if name and tag_type:
            tag = {"name": name, "type": tag_type, "area": snap7.types.Areas.PE, "byte": 0, "bit": 0}
            tags.append(tag)
            row_count = self.tag_table.rowCount()
            self.tag_table.insertRow(row_count)
            self.tag_table.setItem(row_count, 0, QTableWidgetItem(name))
            self.tag_table.setItem(row_count, 1, QTableWidgetItem(tag_type))

    def remove_tag(self):
        selected_rows = self.tag_table.selectionModel().selectedRows()
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            del tags[row]
            self.tag_table.removeRow(row)

    def update_tags(self):
        pass
        plc = snap7.client.Client()
        try:
            plc.connect(IP_ADDRESS, RACK, SLOT)

            for i, tag in enumerate(tags):
                value = read_tag(plc, tag)
                self.tag_table.setItem(i, 2, QTableWidgetItem(str(value)))

            plc.disconnect()
        except RuntimeError as e:
            QMessageBox.critical(self, "Error", str(e))

def read_tag(plc, tag):
    if tag["type"] == "bool":
        data = plc.read_area(tag["area"], 0, tag["byte"], 1)
        return get_bool(data, 0, tag["bit"])
    elif tag["type"] == "int":
        data = plc.read_area(tag["area"], 0, tag["byte"], 2)
        return get_int(data, 0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

