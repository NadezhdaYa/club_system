from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QFormLayout, QLineEdit,
                             QComboBox, QDateTimeEdit, QTextEdit, QPushButton,
                             QMessageBox)
from PyQt6.QtCore import Qt, QDateTime
from sqlalchemy.orm import Session
from models import TrainingSession
from services import SchedulingService
from repositories import StaffRepository, ServiceRepository, ClientRepository


class TrainingForm(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        self.setWindowTitle("Добавить тренировку")
        self.resize(400, 500)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.client_combo = QComboBox()
        self.staff_combo = QComboBox()
        self.service_combo = QComboBox()

        self.start_dt = QDateTimeEdit()
        self.start_dt.setDateTime(QDateTime.currentDateTime())
        self.start_dt.setDisplayFormat("yyyy-MM-dd HH:mm")

        self.end_dt = QDateTimeEdit()
        self.end_dt.setDateTime(QDateTime.currentDateTime().addSecs(3600))
        self.end_dt.setDisplayFormat("yyyy-MM-dd HH:mm")

        self.notes_edit = QTextEdit()

        form.addRow("Клиент:", self.client_combo)
        form.addRow("Тренер:", self.staff_combo)
        form.addRow("Услуга:", self.service_combo)
        form.addRow("Начало:", self.start_dt)
        form.addRow("Конец:", self.end_dt)
        form.addRow("Заметки:", self.notes_edit)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save_training)

        layout.addLayout(form)
        layout.addWidget(btn_save)
        self.setLayout(layout)

        self.load_combos()

    def load_combos(self):
        session = self.session_factory()
        try:
            clients = ClientRepository.get_all(session)
            for c in clients:
                self.client_combo.addItem(c.full_name, c.id)

            staff = StaffRepository.get_active(session)
            for s in staff:
                self.staff_combo.addItem(s.full_name, s.id)

            services = ServiceRepository.get_active(session)
            for s in services:
                self.service_combo.addItem(s.name, s.id)
        finally:
            session.close()

    def save_training(self):
        session = self.session_factory()
        try:
            staff_id = self.staff_combo.currentData()
            start_at = self.start_dt.dateTime().toPyDateTime()
            end_at = self.end_dt.dateTime().toPyDateTime()

            if end_at <= start_at:
                QMessageBox.warning(self, "Ошибка", "Время окончания должно быть позже начала.")
                return

            if not SchedulingService.check_staff_conflict(session, staff_id, start_at, end_at):
                QMessageBox.warning(self, "Конфликт", "У тренера уже есть тренировка в это время.")
                return

            ts = TrainingSession(
                service_id=self.service_combo.currentData(),
                staff_id=staff_id,
                client_id=self.client_combo.currentData(),
                start_at=start_at,
                end_at=end_at,
                status="planned",
                is_actual=True
            )
            session.add(ts)
            session.commit()
            QMessageBox.information(self, "Готово", "Тренировка добавлена.")
            self.close()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()