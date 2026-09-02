from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                              QTableWidget, QTableWidgetItem, QPushButton,
                              QComboBox, QLabel, QDateEdit, QMessageBox,
                              QHeaderView)
from PyQt6.QtCore import QDate, Qt
from app.repositories import ReportRepository, StaffRepository, ClientRepository
from datetime import datetime


class ReportsWindow(QWidget):
    def __init__(self, session_factory):
        super().__init__()
        self.session_factory = session_factory
        layout = QVBoxLayout()

        tabs = QTabWidget()

        tabs.addTab(self._tab_clients_by_status(), "Клиенты по статусу")
        tabs.addTab(self._tab_staff_schedule(), "Расписание тренера")
        tabs.addTab(self._tab_client_history(), "История посещений")

        layout.addWidget(tabs)
        self.setLayout(layout)

    # ── Вкладка 1: Клиенты по статусу ──

    def _tab_clients_by_status(self):
        tab = QWidget()
        layout = QVBoxLayout()

        btn = QPushButton("Сформировать отчёт")
        btn.clicked.connect(self._load_clients_by_status)
        layout.addWidget(btn)

        self.table_status = QTableWidget()
        self.table_status.setColumnCount(2)
        self.table_status.setHorizontalHeaderLabels(["Статус", "Количество"])
        self.table_status.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_status)

        # Детализация
        self.table_status_detail = QTableWidget()
        self.table_status_detail.setColumnCount(5)
        self.table_status_detail.setHorizontalHeaderLabels(
            ["ID", "ФИО", "Телефон", "E-mail", "Дата создания"]
        )
        self.table_status_detail.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Детализация по выбранному статусу:"))
        layout.addWidget(self.table_status_detail)

        self.table_status.cellClicked.connect(self._on_status_row_click)

        tab.setLayout(layout)
        self.load_status_combo_data()
        return tab

    def load_status_combo_data(self):
        pass  # данные грузятся по кнопке

    def _load_clients_by_status(self):
        session = self.session_factory()
        try:
            rows = ReportRepository.clients_by_status(session)
            self.table_status.setRowCount(0)
            for r in rows:
                row = self.table_status.rowCount()
                self.table_status.insertRow(row)
                self.table_status.setItem(row, 0, QTableWidgetItem(r.status))
                self.table_status.setItem(row, 1, QTableWidgetItem(str(r.count)))
        finally:
            session.close()

    def _on_status_row_click(self, row, _col):
        status = self.table_status.item(row, 0).text()
        session = self.session_factory()
        try:
            clients = ClientRepository.get_by_status(session, status)
            self.table_status_detail.setRowCount(0)
            for c in clients:
                r = self.table_status_detail.rowCount()
                self.table_status_detail.insertRow(r)
                self.table_status_detail.setItem(r, 0, QTableWidgetItem(str(c.id)))
                self.table_status_detail.setItem(r, 1, QTableWidgetItem(c.full_name))
                self.table_status_detail.setItem(r, 2, QTableWidgetItem(c.phone or ""))
                self.table_status_detail.setItem(r, 3, QTableWidgetItem(c.email or ""))
                self.table_status_detail.setItem(r, 4,
                    QTableWidgetItem(c.created_at.strftime("%Y-%m-%d") if c.created_at else ""))
        finally:
            session.close()

    # ── Вкладка 2: Расписание тренера ──

    def _tab_staff_schedule(self):
        tab = QWidget()
        layout = QVBoxLayout()

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Тренер:"))
        self.staff_combo_report = QComboBox()

        date_from = QDateEdit()
        date_from.setDate(QDate(2026, 1, 1))
        date_from.setDisplayFormat("yyyy-MM-dd")
        self.date_from_staff = date_from

        date_to = QDateEdit()
        date_to.setDate(QDate(2026, 12, 31))
        date_to.setDisplayFormat("yyyy-MM-dd")
        self.date_to_staff = date_to

        ctrl.addWidget(self.staff_combo_report)
        ctrl.addWidget(QLabel("С:"))
        ctrl.addWidget(date_from)
        ctrl.addWidget(QLabel("По:"))
        ctrl.addWidget(date_to)

        btn = QPushButton("Сформировать")
        btn.clicked.connect(self._load_staff_schedule)
        ctrl.addWidget(btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.table_staff_schedule = QTableWidget()
        self.table_staff_schedule.setColumnCount(5)
        self.table_staff_schedule.setHorizontalHeaderLabels(
            ["ID", "Начало", "Конец", "Услуга", "Клиент"]
        )
        self.table_staff_schedule.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_staff_schedule)

        # Заполняем тренеров
        session = self.session_factory()
        try:
            staff = StaffRepository.get_active(session)
            for s in staff:
                self.staff_combo_report.addItem(s.full_name, s.id)
        finally:
            session.close()

        tab.setLayout(layout)
        return tab

    def _load_staff_schedule(self):
        staff_id = self.staff_combo_report.currentData()
        if not staff_id:
            QMessageBox.warning(self, "Ошибка", "Выберите тренера.")
            return
        date_from = self.date_from_staff.date().toPyDateTime()
        date_to = self.date_to_staff.date().toPyDateTime()
        session = self.session_factory()
        try:
            rows = ReportRepository.staff_schedule(session, staff_id, date_from, date_to)
            self.table_staff_schedule.setRowCount(0)
            for r in rows:
                row = self.table_staff_schedule.rowCount()
                self.table_staff_schedule.insertRow(row)
                self.table_staff_schedule.setItem(row, 0, QTableWidgetItem(str(r.id)))
                self.table_staff_schedule.setItem(row, 1, QTableWidgetItem(r.start_at.strftime("%Y-%m-%d %H:%M")))
                self.table_staff_schedule.setItem(row, 2, QTableWidgetItem(r.end_at.strftime("%Y-%m-%d %H:%M")))
                self.table_staff_schedule.setItem(row, 3, QTableWidgetItem(r.service_name))
                self.table_staff_schedule.setItem(row, 4, QTableWidgetItem(r.client_name))
        finally:
            session.close()

    # ── Вкладка 3: История посещений клиента ──

    def _tab_client_history(self):
        tab = QWidget()
        layout = QVBoxLayout()

        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Клиент:"))
        self.client_combo_report = QComboBox()

        btn = QPushButton("Сформировать")
        btn.clicked.connect(self._load_client_history)
        ctrl.addWidget(self.client_combo_report)
        ctrl.addWidget(btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        self.table_history = QTableWidget()
        self.table_history.setColumnCount(5)
        self.table_history.setHorizontalHeaderLabels(
            ["Дата начала", "Дата окончания", "Статус", "Услуга", "Тренер"]
        )
        self.table_history.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table_history)

        # Заполняем клиентов
        session = self.session_factory()
        try:
            clients = ClientRepository.get_all(session)
            for c in clients:
                self.client_combo_report.addItem(c.full_name, c.id)
        finally:
            session.close()

        tab.setLayout(layout)
        return tab

    def _load_client_history(self):
        client_id = self.client_combo_report.currentData()
        if not client_id:
            QMessageBox.warning(self, "Ошибка", "Выберите клиента.")
            return
        session = self.session_factory()
        try:
            rows = ReportRepository.client_visit_history(session, client_id)
            self.table_history.setRowCount(0)
            for r in rows:
                row = self.table_history.rowCount()
                self.table_history.insertRow(row)
                self.table_history.setItem(row, 0, QTableWidgetItem(r.start_at.strftime("%Y-%m-%d %H:%M")))
                self.table_history.setItem(row, 1, QTableWidgetItem(r.end_at.strftime("%Y-%m-%d %H:%M")))
                self.table_history.setItem(row, 2, QTableWidgetItem(r.status))
                self.table_history.setItem(row, 3, QTableWidgetItem(r.service_name))
                self.table_history.setItem(row, 4, QTableWidgetItem(r.staff_name))
        finally:
            session.close()