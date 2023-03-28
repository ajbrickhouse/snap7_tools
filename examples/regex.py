import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit
from PyQt5.QtGui import QRegExpValidator, QKeyEvent
from PyQt5.QtCore import QRegExp

class CapitalizingLineEdit(QLineEdit):
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.text().isalpha():
            event = QKeyEvent(
                event.type(),
                event.key(),
                event.modifiers(),
                event.text().upper(),
                event.isAutoRepeat(),
                event.count(),
                # event.text().replace("%", "")
            )
        super().keyPressEvent(event)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("QLineEdit with Regex Validator")

        # Create a QVBoxLayout to organize widgets
        layout = QVBoxLayout()

        # Create a QLineEdit
        line_edit = CapitalizingLineEdit()

        # Set the regex pattern
        regex_pattern = r'^%[IQM](?:[BW]?[0-9]{1,16}(?:\.[0-7])?|B[01])$|^%[QW][1-9]\d?$|^%[M][B1]|[MW][1-9]\d?\d?$'

        # Create a QRegExpValidator with the regex pattern
        validator = QRegExpValidator(QRegExp(regex_pattern))

        # Set the validator for the QLineEdit
        line_edit.setValidator(validator)

        # Add QLineEdit to the layout
        layout.addWidget(line_edit)

        # Set the layout for the main window
        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
