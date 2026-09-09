from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                              QLineEdit, QDateEdit, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from app.repositories import ClientRepository

class ClientsWindow(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить клиента")
        btn_add.clicked.connect(self.add_client)
        btn_training = QPushButton("Добавить тренировку")
        btn_training.clicked.connect(self.open_training_form)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_training)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Телефон", "E-mail", "Статус", "Дата рождения", "Действия"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def status_color(self, status):
        mapping = {
            "active": QColor(144, 238, 144),
            "new": QColor(255, 255, 0),
            "frozen": QColor(173, 216, 230),
            "closed": QColor(255, 182, 193),
        }
        return mapping.get(status, QColor(255, 255, 255))

    def load_data(self):
        session = self.session_factory()
        try:
            clients = ClientRepository.get_all(session)
            self.table.setRowCount(0)
            for c in clients:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(c.id)))
                self.table.setItem(row, 1, QTableWidgetItem(c.full_name))
                self.table.setItem(row, 2, QTableWidgetItem(c.phone or ""))
                self.table.setItem(row, 3, QTableWidgetItem(c.email or ""))

                status_item = QTableWidgetItem(c.status)
                status_item.setBackground(self.status_color(c.status))
                self.table.setItem(row, 4, status_item)

                bd_str = c.birth_date.isoformat() if c.birth_date else ""
                self.table.setItem(row, 5, QTableWidgetItem(bd_str))

                edit_btn = QPushButton("Изменить")
                edit_btn.setFixedWidth(80)
                edit_btn.clicked.connect(lambda checked, cid=c.id: self.edit_client(cid))
                self.table.setCellWidget(row, 6, edit_btn)
        finally:
            session.close()

    def add_client(self):
        dialog = ClientDialog(self.session_factory, self)
        dialog.exec()
        self.load_data()

    def edit_client(self, client_id):
        dialog = ClientDialog(self.session_factory, self, client_id=client_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def open_training_form(self):
        from app.ui.training_form import TrainingForm
        form = TrainingForm(self.session_factory)
        form.exec()

class ClientDialog(QDialog):
    def __init__(self, session_factory, parent=None, client_id=None):
        super().__init__(parent)
        self.session_factory = session_factory
        self.client_id = client_id
        self.is_edit = client_id is not None
        title = "Редактировать клиента" if self.is_edit else "Добавить клиента"
        self.setWindowTitle(title)
        self.resize(350, 300)

        layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.birth_edit = QDateEdit()
        self.birth_edit.setDisplayFormat("yyyy-MM-dd")
        #self.birth_edit.setDate(QDate(2000, 1, 1))

        layout.addRow("ФИО *:", self.name_edit)
        layout.addRow("Телефон:", self.phone_edit)
        layout.addRow("E-mail:", self.email_edit)
        layout.addRow("Дата рождения:", self.birth_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)
        self.setLayout(layout)

        if self.is_edit:
            # Загружаем данные
            session = self.session_factory()
            try:
                client = ClientRepository.get_by_id(session, client_id)
                if not client:
                    QMessageBox.critical(self, "Ошибка", "Клиент не найден")
                    self.reject()
                    return
                self.name_edit.setText(client.full_name)
                self.phone_edit.setText(client.phone or "")
                self.email_edit.setText(client.email or "")
                if client.birth_date:
                    self.birth_edit.setDate(QDate.fromString(client.birth_date.isoformat(), "yyyy-MM-dd"))
            finally:
                session.close()

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "ФИО обязательно.")
            return
        session = self.session_factory()
        try:
            if self.is_edit:
                ClientRepository.update(session, self.client_id,
                                        full_name=name,
                                        phone=self.phone_edit.text().strip() or None,
                                        email=self.email_edit.text().strip() or None,
                                        birth_date=self.birth_edit.date().toPyDate())
                QMessageBox.information(self, "Готово", "Клиент обновлён.")
            else:
                ClientRepository.create(
                    session, full_name=name,
                    phone=self.phone_edit.text().strip() or None,
                    email=self.email_edit.text().strip() or None,
                    birth_date=self.birth_edit.date().toPyDate()
                )
                QMessageBox.information(self, "Готово", "Клиент добавлен.")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()