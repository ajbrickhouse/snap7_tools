import sys
import snap7
from snap7.util import *
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QStatusBar, QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QAction
from PyQt5.QtCore import QThread, pyqtSignal, QSettings, QTimer
from PyQt5.QtGui import QIcon
import json


# Default settings. These will be overwritten by the settings file if it exists.
IP_ADDRESS = "192.168.0.1"
RACK = 0
SLOT = 1

class TagUpdateWorker(QThread):
    '''Worker thread that reads the tags from the PLC and updates the table'''

    update_tag_signal = pyqtSignal(int, str)
    connection_status_signal = pyqtSignal(bool)

    def run(self):
        plc = snap7.client.Client()
        try:
            plc.connect(IP_ADDRESS, RACK, SLOT)
            self.connection_status_signal.emit(True)
        except:
            self.connection_status_signal.emit(False)
            return

        while not self.isInterruptionRequested():
            for i, tag in enumerate(self.tags):
                # value = read_tag(plc, tag)
                # self.update_tag_signal.emit(i, str(value))
                pass
            time.sleep(1)

        plc.disconnect()

class SettingsDialog(QDialog):
    '''Dialog that allows the user to change the IP address, rack, and slot of the PLC'''
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Settings")

        layout = QVBoxLayout()

        self.ip_label = QLabel("IP Address:")
        self.ip_input = QLineEdit(IP_ADDRESS)
        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_input)

        self.rack_label = QLabel("Rack:")
        self.rack_input = QLineEdit(str(RACK))
        layout.addWidget(self.rack_label)
        layout.addWidget(self.rack_input)

        self.slot_label = QLabel("Slot:")
        self.slot_input = QLineEdit(str(SLOT))
        layout.addWidget(self.slot_label)
        layout.addWidget(self.slot_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def get_values(self):
        return self.ip_input.text(), int(self.rack_input.text()), int(self.slot_input.text())

class MainWindow(QMainWindow):
    '''Main window of the application'''
    tags = []

    def __init__(self):
        '''Constructor'''
        super().__init__()

        self.setWindowTitle("PLC Tag Viewer")
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout(self.main_widget)

        self.tag_input_layout = QHBoxLayout()
        self.layout.addLayout(self.tag_input_layout)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings_dialog)
        self.tag_input_layout.addWidget(self.settings_button)

        supported_datatypes = ["Memory", "Datablock"]
        self.type_combo_box = QComboBox()
        self.tag_input_layout.addWidget(self.type_combo_box)
        self.type_combo_box.addItems(supported_datatypes)

        self.name_label = QLabel("Name:")
        self.tag_input_layout.addWidget(self.name_label)

        self.name_input = QLineEdit()
        self.tag_input_layout.addWidget(self.name_input)

        self.address_label = QLabel("Address:")
        self.tag_input_layout.addWidget(self.address_label)

        self.address_input = QLineEdit()
        self.tag_input_layout.addWidget(self.address_input)

        supported_datatypes = ["Bool", "Byte", "Word", "DWord", "LWord", "SInt", "Int", "DInt", "LInt", "USInt", "UInt", "UDInt", "ULInt", "Real", "LReal", "Time", "LTime", "Date", "TIME_OF_DAY", "DATE_AND_TIME", "Char", "WChar", "STring", "WSTring", "Array", "Struct"]
        
        self.type_combo_box = QComboBox()
        self.tag_input_layout.addWidget(self.type_combo_box)
        self.type_combo_box.addItems(supported_datatypes)

        self.add_button = QPushButton("Add Tag")
        self.tag_input_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_tag)

        self.remove_button = QPushButton("Remove Tag")
        self.tag_input_layout.addWidget(self.remove_button)
        # self.remove_button.clicked.connect(self.remove_tag)

        self.start_button = QPushButton("Start Reading")
        self.tag_input_layout.addWidget(self.start_button)
        # self.start_button.clicked.connect(self.start_reading)

        self.stop_button = QPushButton("Stop Reading")
        self.tag_input_layout.addWidget(self.stop_button)
        # self.stop_button.clicked.connect(self.stop_reading)

        self.save_button = QPushButton(QIcon("floppy_disk_icon.svg"), "Save Tags")
        self.tag_input_layout.addWidget(self.save_button)
        # self.save_button.clicked.connect(self.save_tags)

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.tag_table = QTableWidget()
        self.layout.addWidget(self.tag_table)
        self.tag_table.setColumnCount(4)
        self.tag_table.setHorizontalHeaderLabels(["Name", "Address", "Type", "Value"])
        self.tag_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.tag_update_worker = TagUpdateWorker()
        # self.tag_update_worker.update_tag_signal.connect(self.update_tag_value)
        # self.tag_update_worker.connection_status_signal.connect(self.update_connection_status)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")

        # self.load_settings()
        # self.load_tags()

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.check_connection)
        # self.timer.start(1000)

    def open_settings_dialog(self):
        '''Opens the settings dialog'''
        settings_dialog = SettingsDialog(self)
        result = settings_dialog.exec_()
        if result == QDialog.Accepted:
            ip, rack, slot = settings_dialog.get_values()
            global IP_ADDRESS, RACK, SLOT
            IP_ADDRESS = ip
            RACK = rack
            SLOT = slot
            self.save_settings()

    def add_tag_to_table(self, tag):
        '''Create a method to add tags to the table without modifying the global tags list. 
           This method will be used when loading tags from the saved settings'''
        row_count = self.tag_table.rowCount()
        self.tag_table.insertRow(row_count)
        self.tag_table.setItem(row_count, 0, QTableWidgetItem(tag["ip_address"]))
        self.tag_table.setItem(row_count, 1, QTableWidgetItem(tag["name"]))
        self.tag_table.setItem(row_count, 2, QTableWidgetItem(tag["type"]))

    def add_tag(self):
        ip_address = IP_ADDRESS  # You can replace this with a QLineEdit to input the IP address
        name = self.name_input.text()
        tag_type = self.type_input.text()

        if ip_address and name and tag_type:
            tag = {"ip_address": ip_address, "name": name, "type": tag_type, "area": snap7.types.Areas.PE, "byte": 0, "bit": 0}
            self.tags.append(tag)
            self.add_tag_to_table(tag)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

