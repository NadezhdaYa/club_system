import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTabWidget
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL
from app.ui.clients_window import ClientsWindow
from app.ui.staff_window import StaffWindow
from app.ui.services_window import ServicesWindow
from app.ui.schedule_window import ScheduleWindow
from app.ui.reports_window import ReportsWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Спортивный клуб — система учёта")
        self.resize(1000, 700)

        engine = create_engine(DATABASE_URL, echo=False)
        self.session_factory = sessionmaker(bind=engine)

        tabs = QTabWidget()
        tabs.addTab(ClientsWindow(self.session_factory), "Клиенты")
        tabs.addTab(StaffWindow(self.session_factory), "Персонал")
        tabs.addTab(ServicesWindow(self.session_factory), "Услуги")
        tabs.addTab(ScheduleWindow(self.session_factory), "Расписание")
        tabs.addTab(ReportsWindow(self.session_factory), "Отчёты")

        self.setCentralWidget(tabs)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()