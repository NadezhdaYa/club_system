from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                              QLineEdit, QDateEdit, QMessageBox, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor
from app.repositories import ClientRepository

class ClientsWindow(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        layout = QVBoxLayout()

        # Панель кнопок
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

        # Таблица
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

                # Выпадающий список для статуса
                status_combo = QComboBox()
                statuses = ["new", "active", "frozen", "closed"]
                status_combo.addItems(statuses)
                status_combo.setCurrentText(c.status)
                # Сохраняем client_id в пользовательском свойстве комбобокса, чтобы знать, кого обновлять
                status_combo.setProperty("client_id", c.id)
                status_combo.currentTextChanged.connect(lambda text, combo=status_combo: self.on_status_changed(combo))
                self.table.setCellWidget(row, 4, status_combo)

                # Цвет ячейки статуса (под цвет выбранного статуса)
                color = self.status_color(c.status)
                cell = QTableWidgetItem()
                cell.setBackground(color)
                cell.setFlags(cell.flags() & ~Qt.ItemFlag.ItemIsEditable)
                self.table.setItem(row, 4, cell)  # перекрываем, чтобы был фон

                bd_str = c.birth_date.isoformat() if c.birth_date else ""
                self.table.setItem(row, 5, QTableWidgetItem(bd_str))

                # Кнопки в колонке «Действия»
                edit_btn = QPushButton("Изменить")
                edit_btn.setFixedWidth(80)
                edit_btn.clicked.connect(lambda checked, cid=c.id: self.edit_client(cid))

                del_btn = QPushButton("Удалить")
                del_btn.setFixedWidth(80)
                del_btn.setStyleSheet("color: red; font-weight: bold;")
                del_btn.clicked.connect(lambda checked, cid=c.id: self.delete_client(cid))

                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)

                cell_widget = QWidget()
                cell_widget.setLayout(action_layout)
                self.table.setCellWidget(row, 6, cell_widget)  # 6 — индекс колонки «Действия»
        finally:
            session.close()

    def on_status_changed(self, combo: QComboBox):
        client_id = combo.property("client_id")
        new_status = combo.currentText()

        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Изменить статус клиента ID {client_id} на «{new_status}»?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            # Откатим к предыдущему значению, если пользователь нажал «Нет»
            # Для простоты перезагружаем таблицу
            self.load_data()
            return

        session = self.session_factory()
        try:
            ok, msg = ClientRepository.update_status(session, client_id, new_status)
            if ok:
                QMessageBox.information(self, "Готово", "Статус изменён.")
                self.load_data()  # перерисуем таблицу с новыми цветами
            else:
                QMessageBox.warning(self, "Отклонено", msg)
                self.load_data()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))
            self.load_data()
        finally:
            session.close()

    def add_client(self):
        dialog = ClientDialog(self.session_factory, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def edit_client(self, client_id):
        dialog = ClientDialog(self.session_factory, self, client_id=client_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def delete_client(self, client_id: int):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Вы уверены, что хотите удалить клиента с ID {client_id}?\n"
            "Если есть связанные тренировки — удаление будет заблокировано БД.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        session = self.session_factory()
        try:
            ok = ClientRepository.delete(session, client_id)
            if ok:
                QMessageBox.information(self, "Готово", "Клиент удалён.")
                self.load_data()
            else:
                QMessageBox.warning(self, "Ошибка", "Клиент не найден.")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))
        finally:
            session.close()

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
        self.birth_edit.setDate(QDate(2000, 1, 1))

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