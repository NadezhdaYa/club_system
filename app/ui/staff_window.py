from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                              QLineEdit, QCheckBox, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from app.repositories import StaffRepository


class StaffWindow(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        layout = QVBoxLayout()

        # Панель кнопок
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.add_staff)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Телефон", "E-mail", "Должность", "Активен", "Действия"]
        )
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        session = self.session_factory()
        try:
            staff = StaffRepository.get_all(session)
            self.table.setRowCount(0)
            for s in staff:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(s.id)))
                self.table.setItem(row, 1, QTableWidgetItem(s.full_name))
                self.table.setItem(row, 2, QTableWidgetItem(s.phone or ""))
                self.table.setItem(row, 3, QTableWidgetItem(s.email or ""))
                self.table.setItem(row, 4, QTableWidgetItem(s.position or ""))
                active_item = QTableWidgetItem("Да" if s.is_active else "Нет")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 5, active_item)

                edit_btn = QPushButton("Изменить")
                edit_btn.setFixedWidth(80)
                edit_btn.clicked.connect(lambda checked, sid=s.id: self.edit_staff(sid))
                self.table.setCellWidget(row, 6, edit_btn)
        finally:
            session.close()

    def add_staff(self):
        dialog = StaffDialog(self.session_factory, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def edit_staff(self, staff_id):
        dialog = StaffDialog(self.session_factory, self, staff_id=staff_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

class StaffDialog(QDialog):
    def __init__(self, session_factory, parent=None, staff_id=None):
        super().__init__(parent)
        self.session_factory = session_factory
        self.staff_id = staff_id
        self.is_edit = staff_id is not None
        title = "Редактировать сотрудника" if self.is_edit else "Добавить сотрудника"
        self.setWindowTitle(title)
        self.resize(350, 300)

        layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.phone_edit = QLineEdit()
        self.email_edit = QLineEdit()
        self.position_edit = QLineEdit()
        self.active_check = QCheckBox()
        self.active_check.setChecked(True)

        layout.addRow("ФИО *:", self.name_edit)
        layout.addRow("Телефон:", self.phone_edit)
        layout.addRow("E-mail:", self.email_edit)
        layout.addRow("Должность:", self.position_edit)
        layout.addRow("Активен:", self.active_check)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)
        self.setLayout(layout)

        if self.is_edit:
            session = self.session_factory()
            try:
                s = StaffRepository.get_by_id(session, staff_id)
                if not s:
                    QMessageBox.critical(self, "Ошибка", "Сотрудник не найден")
                    self.reject()
                    return
                self.name_edit.setText(s.full_name)
                self.phone_edit.setText(s.phone or "")
                self.email_edit.setText(s.email or "")
                self.position_edit.setText(s.position or "")
                self.active_check.setChecked(s.is_active)
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
                StaffRepository.update(session, self.staff_id,
                                       full_name=name,
                                       phone=self.phone_edit.text().strip() or None,
                                       email=self.email_edit.text().strip() or None,
                                       position=self.position_edit.text().strip() or None,
                                       is_active=self.active_check.isChecked())
                QMessageBox.information(self, "Готово", "Сотрудник обновлён.")
            else:
                StaffRepository.create(
                    session, full_name=name,
                    phone=self.phone_edit.text().strip() or None,
                    email=self.email_edit.text().strip() or None,
                    position=self.position_edit.text().strip() or None,
                    is_active=self.active_check.isChecked()
                )
                QMessageBox.information(self, "Готово", "Сотрудник добавлен.")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()