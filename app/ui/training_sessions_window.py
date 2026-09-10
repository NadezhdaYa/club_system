from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                             QComboBox, QDateTimeEdit, QLineEdit, QMessageBox,
                             QHeaderView, QSpinBox)
from PyQt6.QtCore import Qt, QDateTime
from app.repositories import (TrainingSessionRepository, ClientRepository,
                              StaffRepository, ServiceRepository)
from datetime import datetime


class TrainingSessionsWindow(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        layout = QVBoxLayout()

        # Панель кнопок
        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить тренировку")
        btn_add.clicked.connect(self.add_training)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()

        # Таблица
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "ID", "Дата начала", "Дата окончания", "Тренер",
            "Клиент", "Услуга", "Статус", "Действия"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setAlternatingRowColors(True)

        layout.addLayout(btn_layout)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_data()

    def fmt_dt(self, dt):
        if not dt:
            return ""
        if isinstance(dt, str):
            return dt
        return dt.strftime("%Y-%m-%d %H:%M")

    def load_data(self):
        session = self.session_factory()
        try:
            trainings = TrainingSessionRepository.get_all(session)
            self.table.setRowCount(0)
            for t in trainings:
                row = self.table.rowCount()
                self.table.insertRow(row)

                self.table.setItem(row, 0, QTableWidgetItem(str(t.id)))
                self.table.setItem(row, 1, QTableWidgetItem(self.fmt_dt(t.start_at)))
                self.table.setItem(row, 2, QTableWidgetItem(self.fmt_dt(t.end_at)))
                self.table.setItem(row, 3, QTableWidgetItem(
                    t.staff.full_name if t.staff else "—"
                ))
                self.table.setItem(row, 4, QTableWidgetItem(
                    t.client.full_name if t.client else "—"
                ))
                self.table.setItem(row, 5, QTableWidgetItem(
                    t.service.name if t.service else "—"
                ))

                status_item = QTableWidgetItem(t.status)
                status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 6, status_item)

                # Кнопки
                edit_btn = QPushButton("Изменить")
                edit_btn.setFixedWidth(80)
                edit_btn.clicked.connect(lambda checked, tid=t.id: self.edit_training(tid))

                del_btn = QPushButton("Удалить")
                del_btn.setFixedWidth(80)
                del_btn.setStyleSheet("color: red; font-weight: bold;")
                del_btn.clicked.connect(lambda checked, tid=t.id: self.delete_training(tid))

                action_layout = QHBoxLayout()
                action_layout.setContentsMargins(0, 0, 0, 0)
                action_layout.addWidget(edit_btn)
                action_layout.addWidget(del_btn)

                cell_widget = QWidget()
                cell_widget.setLayout(action_layout)
                self.table.setCellWidget(row, 7, cell_widget)
        finally:
            session.close()

    def add_training(self):
        dialog = TrainingDialog(self.session_factory, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def edit_training(self, training_id):
        dialog = TrainingDialog(self.session_factory, self, training_id=training_id)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_data()

    def delete_training(self, training_id):
        reply = QMessageBox.question(
            self,
            "Подтверждение",
            f"Удалить тренировку с ID {training_id}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        session = self.session_factory()
        try:
            ok = TrainingSessionRepository.delete(session, training_id)
            if ok:
                QMessageBox.information(self, "Готово", "Тренировка удалена.")
                self.load_data()
            else:
                QMessageBox.warning(self, "Ошибка", "Тренировка не найдена.")
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка БД", str(e))
        finally:
            session.close()


class TrainingDialog(QDialog):
    def __init__(self, session_factory, parent=None, training_id=None):
        super().__init__(parent)
        self.session_factory = session_factory
        self.training_id = training_id
        self.is_edit = training_id is not None
        title = "Редактировать тренировку" if self.is_edit else "Добавить тренировку"
        self.setWindowTitle(title)
        self.resize(420, 480)

        layout = QFormLayout()

        # Выпадающие списки
        self.client_combo = QComboBox()
        self.staff_combo = QComboBox()
        self.service_combo = QComboBox()
        self.status_combo = QComboBox()
        self.status_combo.addItems(["planned", "completed", "cancelled"])

        # Поля даты/времени
        self.start_edit = QDateTimeEdit()
        self.start_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDateTime(QDateTime.currentDateTime())

        self.end_edit = QDateTimeEdit()
        self.end_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDateTime(QDateTime.currentDateTime().addSecs(3600))

        # Заметки
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("Необязательно")

        # Заполняем выпадающие списки
        session = self.session_factory()
        try:
            clients = ClientRepository.get_all(session)
            for c in clients:
                self.client_combo.addItem(c.full_name, c.id)

            staff = StaffRepository.get_active(session)
            for s in staff:
                self.staff_combo.addItem(s.full_name, s.id)

            services = ServiceRepository.get_active(session)
            for svc in services:
                self.service_combo.addItem(svc.name, svc.id)
        finally:
            session.close()

        layout.addRow("Клиент *:", self.client_combo)
        layout.addRow("Тренер *:", self.staff_combo)
        layout.addRow("Услуга *:", self.service_combo)
        layout.addRow("Начало *:", self.start_edit)
        layout.addRow("Конец *:", self.end_edit)
        layout.addRow("Статус:", self.status_combo)
        layout.addRow("Заметки:", self.notes_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)
        self.setLayout(layout)

        # При редактировании — загружаем данные
        if self.is_edit:
            session = self.session_factory()
            try:
                t = TrainingSessionRepository.get_by_id(session, training_id)
                if not t:
                    QMessageBox.critical(self, "Ошибка", "Тренировка не найдена")
                    self.reject()
                    return

                self.client_combo.setCurrentIndex(self.client_combo.findData(t.client_id))
                self.staff_combo.setCurrentIndex(self.staff_combo.findData(t.staff_id))
                self.service_combo.setCurrentIndex(self.service_combo.findData(t.service_id))

                if t.start_at:
                    self.start_edit.setDateTime(QDateTime.fromString(
                        t.start_at.strftime("%Y-%m-%d %H:%M"), "yyyy-MM-dd HH:mm"
                    ))
                if t.end_at:
                    self.end_edit.setDateTime(QDateTime.fromString(
                        t.end_at.strftime("%Y-%m-%d %H:%M"), "yyyy-MM-dd HH:mm"
                    ))

                self.status_combo.setCurrentText(t.status)
                self.notes_edit.setText(t.notes or "")
            finally:
                session.close()

    def save(self):
        client_id = self.client_combo.currentData()
        staff_id = self.staff_combo.currentData()
        service_id = self.service_combo.currentData()

        if not client_id or not staff_id or not service_id:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента, тренера и услугу.")
            return

        start_dt = self.start_edit.dateTime().toPyDateTime()
        end_dt = self.end_edit.dateTime().toPyDateTime()

        if end_dt <= start_dt:
            QMessageBox.warning(self, "Ошибка", "Время окончания должно быть позже начала.")
            return

        session = self.session_factory()
        try:
            # Проверка конфликта тренера
            exclude = self.training_id if self.is_edit else None
            conflicts = TrainingSessionRepository.check_conflict(
                session, staff_id, start_dt, end_dt, exclude_id=exclude
            )
            if conflicts:
                names = "\n".join(
                    f"  • {c.start_at.strftime('%Y-%m-%d %H:%M')} – "
                    f"{c.end_at.strftime('%H:%M')}"
                    for c in conflicts
                )
                QMessageBox.warning(
                    self,
                    "Конфликт расписания",
                    f"У тренера уже есть тренировка(и) в это время:\n{names}"
                )
                return

            if self.is_edit:
                TrainingSessionRepository.update(
                    session, self.training_id,
                    client_id=client_id,
                    staff_id=staff_id,
                    service_id=service_id,
                    start_at=start_dt,
                    end_at=end_dt,
                    status=self.status_combo.currentText(),
                    notes=self.notes_edit.text().strip() or None,
                )
                QMessageBox.information(self, "Готово", "Тренировка обновлена.")
            else:
                TrainingSessionRepository.create(
                    session,
                    client_id=client_id,
                    staff_id=staff_id,
                    service_id=service_id,
                    start_at=start_dt,
                    end_at=end_dt,
                    status=self.status_combo.currentText(),
                    notes=self.notes_edit.text().strip() or None,
                )
                QMessageBox.information(self, "Готово", "Тренировка добавлена.")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()