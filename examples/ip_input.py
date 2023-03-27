import sys
from PyQt5.QtWidgets import QApplication, QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

def calculate_subnet(ip_address, subnet_mask):
    ip_parts = [int(part) for part in ip_address.split('.')]
    mask_parts = [int(part) for part in subnet_mask.split('.')]
    
    subnet = [str(ip & mask) for ip, mask in zip(ip_parts, mask_parts)]
    return '.'.join(subnet)

class IPAddressLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        # Regular expression for IPv4 addresses
        ip_regex = QRegExp("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$")
        ip_validator = QRegExpValidator(ip_regex, self)
        self.setValidator(ip_validator)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.ip_address_input = IPAddressLineEdit()
        layout.addWidget(self.ip_address_input)

        self.ip2_address_input = IPAddressLineEdit()
        layout.addWidget(self.ip2_address_input)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
