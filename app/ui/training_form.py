from PyQt6.QtWidgets import QWidget, QFormLayout, QLineEdit, QDateTimeEdit, QPushButton, QLabel, QMessageBox
from datetime import datetime, timedelta


class TrainingForm(QWidget):
    def __init__(self, on_save):
        super().__init__()
        self.on_save = on_save
        layout = QFormLayout()

        self.staff_id_input = QLineEdit()
        self.client_id_input = QLineEdit()
        self.service_id_input = QLineEdit()
        self.start_input = QDateTimeEdit(datetime.now())
        self.notes_input = QLineEdit()

        layout.addRow(QLabel("ID тренера"), self.staff_id_input)
        layout.addRow(QLabel("ID клиента"), self.client_id_input)
        layout.addRow(QLabel("ID услуги"), self.service_id_input)
        layout.addRow(QLabel("Начало тренировки"), self.start_input)
        layout.addRow(QLabel("Примечания"), self.notes_input)

        btn = QPushButton("Записать на тренировку")
        btn.clicked.connect(self.save)
        layout.addWidget(btn)
        self.setLayout(layout)

    def save(self):
        try:
            staff_id = int(self.staff_id_input.text())
            client_id = int(self.client_id_input.text())
            service_id = int(self.service_id_input.text())
            start = self.start_input.dateTime().toPyDateTime()
            end = start + timedelta(minutes=60)  # для примера длительность 60 мин
            notes = self.notes_input.text()
            self.on_save(staff_id, client_id, service_id, start, end, notes)
        except ValueError:
            QMessageBox.critical(self, "Ошибка", "Проверьте числовые поля")