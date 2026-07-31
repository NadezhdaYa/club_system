import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QFormLayout,
                             QLineEdit, QDateEdit, QMessageBox, QLabel, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from datetime import date
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from app.models import Base, Client

DATABASE_URL = "postgresql+psycopg2://postgres:NvSTS2@localhost:5432/club_db"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class ClientsWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Учёт клиентов спортивного клуба")
        self.resize(900, 600)

        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout()

        # Форма добавления
        form_group = QWidget()
        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.phone_input = QLineEdit()
        self.email_input = QLineEdit()
        self.birth_input = QDateEdit(QDate.currentDate())
        self.birth_input.setCalendarPopup(True)

        form_layout.addRow("ФИО:", self.name_input)
        form_layout.addRow("Телефон:", self.phone_input)
        form_layout.addRow("E-mail:", self.email_input)
        form_layout.addRow("Дата рождения:", self.birth_input)

        add_btn = QPushButton("Добавить клиента")
        add_btn.clicked.connect(self.add_client)
        form_layout.addWidget(add_btn)
        form_group.setLayout(form_layout)

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "ФИО", "Телефон", "E-mail", "Дата рождения", "Статус"])

        # Настройка ширины колонок
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)  # запретить редактирование

        # Кнопки управления таблицей
        btn_layout = QHBoxLayout()
        refresh_btn = QPushButton("Обновить")
        refresh_btn.clicked.connect(self.load_clients)
        delete_btn = QPushButton("Деактивировать (статус closed)")
        delete_btn.clicked.connect(self.deactivate_selected)

        btn_layout.addWidget(refresh_btn)
        btn_layout.addWidget(delete_btn)

        main_layout.addWidget(form_group)
        main_layout.addWidget(self.table)
        main_layout.addLayout(btn_layout)
        central.setLayout(main_layout)

        self.load_clients()

    def get_session(self):
        return SessionLocal()

    def load_clients(self):
        self.table.setRowCount(0)
        try:
            with self.get_session() as session:
                clients = session.query(Client).all()
                if not clients:
                    self.table.setRowCount(0)
                    self.table.setItem(0, 0, QTableWidgetItem("Нет клиентов"))
                    self.table.setSpan(0, 0, 1, 6) # обьединить все колонки в одну ячейку
                    return

                for c in clients:
                    row_pos = self.table.rowCount()
                    self.table.insertRow(row_pos)
                    self.table.setItem(row_pos, 0, QTableWidgetItem(str(c.id)))
                    self.table.setItem(row_pos, 1, QTableWidgetItem(c.full_name))
                    self.table.setItem(row_pos, 2, QTableWidgetItem(c.phone or ""))
                    self.table.setItem(row_pos, 3, QTableWidgetItem(c.email or ""))
                    birth_str = c.birth_date.strftime("%d.%m.%Y") if c.birth_date else ""
                    self.table.setItem(row_pos, 4, QTableWidgetItem(birth_str))

                    # Цветной статус
                    status_item = QTableWidgetItem(c.status)
                    if c.status == "active":
                        status_item.setForeground(Qt.GlobalColor.green)
                    elif c.status == "closed":
                        status_item.setForeground(Qt.GlobalColor.red)
                    else:
                        status_item.setForeground(Qt.GlobalColor.gray)

                    self.table.setItem(row_pos, 5, status_item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки", str(e))

    def add_client(self):
        name = self.name_input.text().strip()
        phone = self.phone_input.text().strip() or None
        email = self.email_input.text().strip() or None
        birth = self.birth_input.date().toPyDate()  # QDate -> date

        if not name:
            QMessageBox.warning(self, "Ошибка", "Укажите ФИО")
            return

        try:
            with self.get_session() as session:
                client = Client(
                    full_name=name,
                    phone=phone,
                    email=email,
                    birth_date=birth,
                    status="new"
                )
                session.add(client)
                session.commit()
                QMessageBox.information(self, "Успех", "Клиент добавлен")
                self.load_clients()
                # очистка формы
                self.name_input.clear()
                self.phone_input.clear()
                self.email_input.clear()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))

    def deactivate_selected(self):
        rows = self.table.selectedItems()
        if not rows:
            QMessageBox.warning(self, "Внимание", "Выберите строку в таблице")
            return
        row = rows[0].row()
        client_id = int(self.table.item(row, 0).text())

        try:
            with self.get_session() as session:
                client = session.get(Client, client_id)
                if not client:
                    QMessageBox.warning(self, "Не найдено", "Клиент не найден")
                    return
                client.status = "closed"
                session.commit()
                QMessageBox.information(self, "Готово", "Клиент деактивирован")
                self.load_clients()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))