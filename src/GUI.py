from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QDialog, QVBoxLayout, QLabel


class GUI:
    def __init__(self):
        self.Form, self.Window = uic.loadUiType("res/GUI.ui")
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        self.app = QApplication([])
        self.window = self.Window()
        self.form = self.Form()
        self.form.setupUi(self.window)
        self.center()
        # Setup widgets
        self.__setup_interface()
        # Assign event handlers
        self.__add_handlers()

    def center(self):
        frame_gm = self.window.frameGeometry()
        screen = QApplication.desktop().screenNumber(
            QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(screen).center()
        frame_gm.moveCenter(center_point)
        self.window.move(frame_gm.topLeft())

    def __setup_interface(self):
        self.form.main_widget.setGeometry(0, 0, self.window.width(), self.window.height())

    def __add_handlers(self):
        """
        Assign event handlers for interactive elements.
        """
        self.form.about_menu_btn.triggered.connect(self.about_menu_btn_handler)

    def about_menu_btn_handler(self):
        dialog = QDialog(self.window)
        dialog.setWindowTitle("About")
        dialog.setMinimumSize(300, 100)
        layout = QVBoxLayout()
        msg = QLabel("About deez nuts... GOTTEM ;)")
        layout.addWidget(msg)
        dialog.setLayout(layout)
        dialog.exec()

    def open(self):
        self.window.show()
        self.app.exec_()
