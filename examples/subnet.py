import sys
from PyQt5.QtWidgets import QApplication, QLabel, QLineEdit, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import QRegExp
from PyQt5.QtGui import QRegExpValidator

class IPAddressLineEdit(QLineEdit):
    def __init__(self):
        super().__init__()
        ip_regex = QRegExp("^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\\/([0-9]|[1-2][0-9]|3[0-2]))?$")
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
        self.ip_address_input.textChanged.connect(self.calculate_subnet_mask)

        self.calculate_button = QPushButton("Calculate Subnet Mask")
        self.calculate_button.clicked.connect(self.calculate_subnet_mask)
        layout.addWidget(self.calculate_button)

        self.subnet_mask_label = QLabel()
        layout.addWidget(self.subnet_mask_label)

        self.setLayout(layout)

    def calculate_subnet_mask(self):
        ip_address = self.ip_address_input.text()
        try:
            if '/' not in ip_address:
                self.subnet_mask_label.setText("Invalid input. Please enter an IP address with CIDR notation.")
                return

            ip, prefix_length = ip_address.split('/')
            prefix_length = int(prefix_length)

            mask = (1 << 32) - (1 << (32 - prefix_length))
            subnet_mask = (mask >> 24 & 255, mask >> 16 & 255, mask >> 8 & 255, mask & 255)
            subnet_mask_str = '.'.join(str(octet) for octet in subnet_mask)

            self.subnet_mask_label.setText(f"Subnet Mask: {subnet_mask_str}")
        except ValueError:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
