import sys
from PyQt6.QtWidgets import QApplication
from app.ui.clients_window import ClientsWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ClientsWindow()
    win.show()
    sys.exit(app.exec())