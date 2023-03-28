import re
import sys
import snap7
from snap7 import util
from snap7.util import * 
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QStyledItemDelegate, QHBoxLayout, QLabel, QLineEdit, QPushButton, QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QStatusBar, QDialog, QVBoxLayout, QLabel, QLineEdit, QDialogButtonBox, QAction
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, QTimer
from PyQt5.QtGui import QIcon
import json
# Default settings. These will be overwritten by the settings file if it exists.
IP_ADDRESS = "192.168.0.1"
RACK = 0
SLOT = 1

class dataTypeDelegate(QStyledItemDelegate):
    ''' Delegate for the data type columns '''
    ''' This is used to create a combobox in the table '''

    def createEditor(self, parent, option, index):
        editor = QComboBox(parent)
        # add datatypes available for siemens tia portal v16 plc tags
        siemens_data_types = [
            "Bool",    # Boolean (1 bit)
            "Byte",    # Byte (8 bits)
            "Word",    # Word (16 bits)
            "DWord",   # Double Word (32 bits)
            "LWord",   # Long Word (64 bits)
            "SInt",    # Signed 8-bit integer
            "Int",     # Signed 16-bit integer
            "DInt",    # Signed 32-bit integer
            "LInt",    # Signed 64-bit integer
            "USInt",   # Unsigned 8-bit integer
            "UInt",    # Unsigned 16-bit integer
            "UDInt",   # Unsigned 32-bit integer
            "ULInt",   # Unsigned 64-bit integer
            "Real",    # Floating-point number (32 bits)
            "LReal",   # Floating-point number (64 bits)
            "Time",    # Time duration (32 bits)
            "LTime",   # Time duration (64 bits)
            "Date",    # Calendar date (16 bits)
            "TIME_OF_DAY", # Time of day (32 bits)
            "DATE_AND_TIME", # Combined date and time (64 bits)
            "Char",    # Single ASCII character (8 bits)
            "WChar",   # Single Unicode character (16 bits)
            "STring",  # Variable-length ASCII string
            "WSTring", # Variable-length Unicode string
            "Array",   # Array of specified data type
            "Struct",  # Structure containing multiple data types
        ]
        editor.addItems(siemens_data_types)  # Add available data types
        return editor

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.EditRole)

        if isinstance(editor, QComboBox):
            editor.setCurrentText(value)
        else:
            editor.setText(value)

    def setModelData(self, editor, model, index):
        if isinstance(editor, QComboBox):
            value = editor.currentText()
        else:
            value = editor.text()

        model.setData(index, value, Qt.EditRole)

    def updateEditorGeometry(self, editor, option, index):
        editor.setGeometry(option.rect)

class TagUpdateWorker(QThread):
    '''Worker thread that reads the tags from the PLC and updates the table'''

    update_tag_signal = pyqtSignal(int, str)
    connection_status_signal = pyqtSignal(bool)

    def __init__(self, tags):
        super().__init__()
        self.tags = tags


    def read_tag(self, plc, tag):
        area_mapping = {
            'I': snap7.types.Areas.PE,
            'Q': snap7.types.Areas.PA,
            'M': snap7.types.Areas.MK,
            'IW': snap7.types.Areas.PE,
            'MB': snap7.types.Areas.DB,
            'MW': snap7.types.Areas.CT,
            'QW': snap7.types.Areas.TM
        }

        area = area_mapping.get(tag['area'])
        byte = int(tag['byte'])
        if tag['bit']:
            bit = int(tag['bit'])
            
        tag['type'] = tag['type'].upper()
        try:

            if tag['type'] == 'BOOL':
                data = plc.read_area(area, 0, byte, 1)
                value = util.get_bool(data, 0, bit)
            elif tag['type'] == 'INT':
                data = plc.read_area(area, 0, byte, 2)
                value = util.get_int(data, 0)
            elif tag['type'] == 'DINT':
                data = plc.read_area(area, 0, byte, 4)
                value = util.get_dint(data, 0)
            elif tag['type'] == 'REAL':
                data = plc.read_area(area, 0, byte, 4)
                value = util.get_real(data, 0)
            elif tag['type'] == 'WORD':
                data = plc.read_area(area, 0, byte, 2)
                value = util.get_word(data, 0)
            elif tag['type'] == 'DWORD':
                data = plc.read_area(area, 0, byte, 4)
                value = util.get_dword(data, 0)
            else:
                raise ValueError(f"Unsupported tag type: {tag['type']}")
            
        except ValueError as e:
            print(f"Error reading tag '{tag['name']}': {e}")
            value = None

        return value

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
                try:
                    value = self.read_tag(plc, tag)
                    self.update_tag_signal.emit(i, str(value))
                except:
                    pass
            time.sleep(0.1)

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

        sources = ["Memory", "Datablock"]

        self.source_combo_box = QComboBox()
        self.tag_input_layout.addWidget(self.source_combo_box)
        self.source_combo_box.addItems(sources)

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
        self.remove_button.clicked.connect(self.remove_tag)

        self.start_button = QPushButton("Start Reading")
        self.tag_input_layout.addWidget(self.start_button)
        self.start_button.clicked.connect(self.start_reading)

        self.stop_button = QPushButton("Stop Reading")
        self.tag_input_layout.addWidget(self.stop_button)
        self.stop_button.clicked.connect(self.stop_reading)

        self.save_button = QPushButton(QIcon("floppy_disk_icon.svg"), "Save Tags")
        self.tag_input_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_tags)

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        
        self.tag_table = QTableWidget()
        self.layout.addWidget(self.tag_table)
        self.tag_table.setColumnCount(7)
        self.tag_table.setHorizontalHeaderLabels(["IP", "Name", "Type", "area", "Byte", "Bit", "Value"])
        self.tag_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.tag_table.setItemDelegateForColumn(2, dataTypeDelegate())

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")

        self.load_settings()
        self.load_tags()

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
        self.tag_table.setItem(row_count, 3, QTableWidgetItem(tag["area"]))
        self.tag_table.setItem(row_count, 4, QTableWidgetItem(tag["byte"]))
        self.tag_table.setItem(row_count, 5, QTableWidgetItem(tag["bit"]))

    def add_tag(self):
        ip_address = IP_ADDRESS  # You can replace this with a QLineEdit to input the IP address
        name = self.name_input.text()
        address = self.address_input.text()
        tag_type = self.type_combo_box.currentText()

        pattern = r'%([IQMB][W]?)(\d+)(?:\.(\d))?'

        match = re.match(pattern, address)
        if match:
            area, before_decimal, after_decimal = match.groups()
            print(area, before_decimal, after_decimal)

        if ip_address and address and area and before_decimal and tag_type:
            tag = {"ip_address": ip_address, "name": name, "type": tag_type, "area": area, "byte": before_decimal, "bit": after_decimal}
            self.tags.append(tag)
            self.add_tag_to_table(tag)

        # if ip_address and name and tag_type:
        #     tag = {"ip_address": ip_address, "name": name, "type": tag_type, "area": snap7.types.Areas.PE, "byte": 0, "bit": 0}
        #     self.tags.append(tag)
        #     self.add_tag_to_table(tag)

    def remove_tag(self):
        '''Removes a tag from the table'''
        selected_rows = self.tag_table.selectionModel().selectedRows()
        for index in sorted(selected_rows, reverse=True):
            row = index.row()
            del self.tags[row]
            self.tag_table.removeRow(row)

    def stop_reading(self):
        '''Stops reading the tags'''
        self.tag_update_worker.requestInterruption()
        self.tag_update_worker.wait()
        # self.tag_update_worker.terminate()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.status_bar.showMessage("Disconnected from PLC")

    def start_reading(self):
        '''Starts reading the tags'''
        self.tag_update_worker = TagUpdateWorker(self.tags)
        self.tag_update_worker.update_tag_signal.connect(self.update_tag_value)
        self.tag_update_worker.connection_status_signal.connect(self.update_connection_status)
        self.tag_update_worker.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def update_connection_status(self, connected):
        ''' Updates the connection status in the status bar'''
        if connected:
            self.status_bar.showMessage(f"Connected to {IP_ADDRESS}")
        elif not connected and not self.start_button.isEnabled():
            self.status_bar.showMessage(f"Connection to {IP_ADDRESS} failed")
        else:
            self.status_bar.showMessage("Disconnected")

    def update_tag_value(self, index, value):
        '''Updates the value of a tag in the table'''
        self.tag_table.setItem(index, 6, QTableWidgetItem(value))

    def save_settings(self):
        ''' Saves the settings to the registry '''
        settings = QSettings("testBench.cc", "readMemory")
        settings.setValue("ip_address", IP_ADDRESS)
        settings.setValue("rack", RACK)
        settings.setValue("slot", SLOT)

    def load_settings(self):
        ''' Loads the settings from the registry '''
        settings = QSettings("testBench.cc", "readMemory")
        global IP_ADDRESS, RACK, SLOT
        IP_ADDRESS = settings.value("ip_address", IP_ADDRESS)
        RACK = int(settings.value("rack", RACK))
        SLOT = int(settings.value("slot", SLOT))

    def save_tags(self):
        try:
            settings = QSettings("testBench.cc", "readMemory")
            self.update_global_tags()
            serializable_tags = [tag.copy() for tag in self.tags]
            for tag in serializable_tags:
                tag["area"] = tag["area"]  # Convert the area to an integer
            tags_json = json.dumps(serializable_tags)
            print(tags_json)
            settings.setValue("tags", tags_json)
        except Exception as e:
            print(e)

    def load_tags(self):
        try:
            settings = QSettings("testBench.cc", "readMemory")
            tags_json = settings.value("tags")
            if tags_json:
                loaded_tags = json.loads(tags_json)
                for tag in loaded_tags:
                    tag["area"] = tag["area"]  # Convert the integer back to an area
                self.tags = loaded_tags
                for tag in self.tags:
                    self.add_tag_to_table(tag)
        except Exception as e:
            print(e)

    def update_global_tags(self):
        table_tags = []
        for row in range(self.tag_table.rowCount()):
            items = [self.tag_table.item(row, i) for i in range(6)]

            # replace any none values with an empty string
            items = [item if item else QTableWidgetItem("") for item in items]

            name, tag_type, ip_address, area, byte, bit = (item.text() for item in items)

            print(name, tag_type, ip_address, area, byte, bit)

            # set the tag area, byte and bit depending on the tag type and name
            # a tag named

            tag = {
                "name": name,
                "type": tag_type,
                "ip_address": ip_address,
                "area": area,
                "byte": byte,
                "bit": bit,
            }
            table_tags.append(tag)

        self.tags = table_tags
        print(self.tags)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

