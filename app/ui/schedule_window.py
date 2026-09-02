from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                              QComboBox, QSpinBox, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from app.repositories import ScheduleSlotRepository, StaffRepository
from app.services import SchedulingService

DAYS = {
    1: "Понедельник",
    2: "Вторник",
    3: "Среда",
    4: "Четверг",
    5: "Пятница",
    6: "Суббота",
    7: "Воскресенье",
}


class ScheduleWindow(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить слот")
        btn_add.clicked.connect(self.add_slot)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Тренер", "День недели", "Время", "Макс. клиентов"]
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
            slots = ScheduleSlotRepository.get_all(session)
            self.table.setRowCount(0)
            for slot in slots:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(slot.id)))
                self.table.setItem(row, 1, QTableWidgetItem(slot.staff.full_name))
                self.table.setItem(row, 2, QTableWidgetItem(DAYS.get(slot.day_of_week, str(slot.day_of_week))))
                self.table.setItem(row, 3, QTableWidgetItem(f"{slot.start_time} – {slot.end_time}"))
                self.table.setItem(row, 4, QTableWidgetItem(str(slot.max_clients)))
        finally:
            session.close()

    def add_slot(self):
        dialog = SlotDialog(self.session_factory, self)
        dialog.exec()
        self.load_data()


class SlotDialog(QDialog):
    def __init__(self, session_factory, parent=None):
        super().__init__(parent)
        self.session_factory = session_factory
        self.setWindowTitle("Добавить слот расписания")
        self.resize(350, 300)

        layout = QFormLayout()

        self.staff_combo = QComboBox()
        self.day_combo = QComboBox()
        for d, name in DAYS.items():
            self.day_combo.addItem(name, d)

        self.start_edit = QLineEdit("09:00")
        self.start_edit.setPlaceholderText("ЧЧ:ММ")
        self.end_edit = QLineEdit("10:00")
        self.end_edit.setPlaceholderText("ЧЧ:ММ")
        self.max_spin = QSpinBox()
        self.max_spin.setRange(1, 100)
        self.max_spin.setValue(10)

        # Заполняем тренеров
        session = self.session_factory()
        try:
            staff = StaffRepository.get_active(session)
            for s in staff:
                self.staff_combo.addItem(s.full_name, s.id)
        finally:
            session.close()

        layout.addRow("Тренер *:", self.staff_combo)
        layout.addRow("День недели *:", self.day_combo)
        layout.addRow("Начало (ЧЧ:ММ) *:", self.start_edit)
        layout.addRow("Конец (ЧЧ:ММ) *:", self.end_edit)
        layout.addRow("Макс. клиентов:", self.max_spin)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)
        self.setLayout(layout)

    def save(self):
        staff_id = self.staff_combo.currentData()
        if not staff_id:
            QMessageBox.warning(self, "Ошибка", "Выберите тренера.")
            return
        start = self.start_edit.text().strip()
        end = self.end_edit.text().strip()
        if not start or not end:
            QMessageBox.warning(self, "Ошибка", "Укажите время начала и окончания.")
            return

        session = self.session_factory()
        try:
            ScheduleSlotRepository.create(
                session,
                staff_id=staff_id,
                day_of_week=self.day_combo.currentData(),
                start_time=start,
                end_time=end,
                max_clients=self.max_spin.value()
            )
            QMessageBox.information(self, "Готово", "Слот добавлен.")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()