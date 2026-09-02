from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QDialog, QFormLayout,
                              QLineEdit, QCheckBox, QMessageBox, QHeaderView,
                              QDoubleSpinBox, QSpinBox)
from PyQt6.QtCore import Qt
from app.repositories import ServiceRepository


class ServicesWindow(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        layout = QVBoxLayout()

        btn_layout = QHBoxLayout()
        btn_add = QPushButton("Добавить")
        btn_add.clicked.connect(self.add_service)
        btn_refresh = QPushButton("Обновить")
        btn_refresh.clicked.connect(self.load_data)
        btn_layout.addWidget(btn_add)
        btn_layout.addWidget(btn_refresh)
        btn_layout.addStretch()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["ID", "Название", "Цена (руб.)", "Длительность (мин.)", "Активна"]
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
            services = ServiceRepository.get_all(session)
            self.table.setRowCount(0)
            for s in services:
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(str(s.id)))
                self.table.setItem(row, 1, QTableWidgetItem(s.name))
                self.table.setItem(row, 2, QTableWidgetItem(f"{s.price:.2f}"))
                self.table.setItem(row, 3, QTableWidgetItem(str(s.duration_minutes)))
                active_item = QTableWidgetItem("Да" if s.is_active else "Нет")
                active_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, 4, active_item)
        finally:
            session.close()

    def add_service(self):
        dialog = ServiceDialog(self.session_factory, self)
        dialog.exec()
        self.load_data()


class ServiceDialog(QDialog):
    def __init__(self, session_factory, parent=None):
        super().__init__(parent)
        self.session_factory = session_factory
        self.setWindowTitle("Добавить услугу")
        self.resize(350, 300)

        layout = QFormLayout()
        self.name_edit = QLineEdit()
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setRange(0, 999999)
        self.price_spin.setSuffix(" руб.")
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(1, 600)
        self.duration_spin.setSuffix(" мин.")
        self.active_check = QCheckBox()
        self.active_check.setChecked(True)

        layout.addRow("Название *:", self.name_edit)
        layout.addRow("Цена *:", self.price_spin)
        layout.addRow("Длительность *:", self.duration_spin)
        layout.addRow("Активна:", self.active_check)

        btn_save = QPushButton("Сохранить")
        btn_save.clicked.connect(self.save)
        layout.addRow(btn_save)
        self.setLayout(layout)

    def save(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Ошибка", "Название обязательно.")
            return
        session = self.session_factory()
        try:
            ServiceRepository.create(
                session, name=name,
                price=self.price_spin.value(),
                duration_minutes=self.duration_spin.value(),
                is_active=self.active_check.isChecked()
            )
            QMessageBox.information(self, "Готово", "Услуга добавлена.")
            self.accept()
        except Exception as e:
            session.rollback()
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            session.close()