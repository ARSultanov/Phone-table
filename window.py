import loguru
from PyQt5.QtWidgets import (QApplication, QMainWindow, QGridLayout, QWidget, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QLabel, QSizePolicy, QPushButton,
                             QGroupBox, QHBoxLayout, QDockWidget, QLineEdit, QMessageBox)
from PyQt5.QtCore import QSize, Qt
from database import DBManager as db


class MainTable(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Телефонный справочник")
        self.setGeometry(100, 100, 1225, 600)
        # Создаем центральный виджет и компоновку
        central_widget = QWidget()

        main_layout = QVBoxLayout(central_widget)  # настравиваем вертикальное расположение виджетов

        # Создаем таблицу
        self.table = QTableWidget(self)

        # Добавляем таблицу в компоновку
        main_layout.addWidget(self.table)

        # Нижняя часть приложения
        horizontal_layout = QHBoxLayout()
        main_layout.addLayout(horizontal_layout)

        # Поля ввода
        input_group = QGroupBox("Поля ввода")
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Имя")
        self.surname_input = QLineEdit()
        self.surname_input.setPlaceholderText("Фамилия")
        self.patronymic_input = QLineEdit()
        self.patronymic_input.setPlaceholderText("Отчество")
        self.street_input = QLineEdit()
        self.street_input.setPlaceholderText("Улица")
        self.house_input = QLineEdit()
        self.house_input.setPlaceholderText("Дом")
        self.apartment_input = QLineEdit()
        self.apartment_input.setPlaceholderText("Квартира")
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Телефон")

        input_layout.addWidget(self.name_input)
        input_layout.addWidget(self.surname_input)
        input_layout.addWidget(self.patronymic_input)
        input_layout.addWidget(self.street_input)
        input_layout.addWidget(self.house_input)
        input_layout.addWidget(self.apartment_input)
        input_layout.addWidget(self.phone_input)

        self.input_fields = [self.name_input, self.surname_input, self.patronymic_input,
                        self.street_input, self.house_input, self.apartment_input,
                        self.phone_input]

        horizontal_layout.addWidget(input_group)
        horizontal_layout.addLayout(input_layout)

        # Кнопки
        button_group = QGroupBox("Действия")
        button_layout = QVBoxLayout()
        button_group.setLayout(button_layout)
        self.add_button = QPushButton("Добавить")
        self.add_button.clicked.connect(self.add_row)
        self.update_button = QPushButton("Обновить")
        self.update_button.clicked.connect(self.update_row)
        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.remove_row)
        self.group_name_label = QLabel("Действия")

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)

        horizontal_layout.addWidget(button_group)
        horizontal_layout.addLayout(button_layout)

        #
        self.setCentralWidget(central_widget)
        self.table.cellClicked.connect(self.fill_edit_lines)

        # Заполняем таблицу данными
        # self.table.setItem(0, 0, QTableWidgetItem("Иван"))

        # Создаем экземпляр DBManager
        self.db = db(
            dbname="phone_dict",
            user="postgres",
            password="iilwnm",
            host="localhost",
            port="5432"
        )

        self.load_data_from_db()

    def load_data_from_db(self):
        # Выполняем SQL-запрос для получения данных
        try:
            rows, col_names = self.db.fetch_data()

            # Устанавливаем количество строк и столбцов в таблице
            self.table.setRowCount(len(rows))
            self.table.setColumnCount(len(col_names))
            self.table.setHorizontalHeaderLabels([col_names[0],"Имя", "Фамилия", "Отчество", "Улица", "Здание", "Квартира", "Телефон"])
            # self.table.setHorizontalHeaderLabels(col_names)

            # Заполняем таблицу данными
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    self.table.setItem(i, j, QTableWidgetItem(str(value)))

            # Автоматически подстраиваем размер столбцов и строк таблицы под содержимое
            self.table.resizeColumnsToContents()
            self.table.resizeRowsToContents()

        except Exception as e:
            QMessageBox.critical(self, "Ошибка загрузки данных", str(e))
            loguru.logger.error(f"Ошибка загрузки данных: {e}")

    def fill_edit_lines(self):
        data = {
            1: self.name_input,
            2: self.surname_input,
            3: self.patronymic_input,
            4: self.street_input,
            5: self.house_input,
            6: self.apartment_input,
            7: self.phone_input
        }
        row = self.table.currentRow()
        for i in data.keys():
            data[i].setText(self.table.item(row, i).text().strip() if self.table.item(row, i) else "")
    def add_row(self):
        keys = ["name", "surname", "patronymic", "street", "building", "apartment", "phone"]
        data = {key: field.text() for key, field in zip(keys, self.input_fields)}
        """data = {
                    "name": self.input_fields[0].text(),
                    "surname": self.input_fields[1].text(),
                    "patronymic": self.input_fields[2].text(),
                    "street": self.input_fields[3].text(),
                    "building": self.input_fields[4].text(),
                    "apartment": self.input_fields[5].text(),
                    "phone": self.input_fields[6].text()
                    }"""
        print(data)
        try:
            self.db.insert_data(data)
            self.load_data_from_db()
            QMessageBox.information(self, "Success", "Запись добавлена успешно")
            loguru.logger.info(f"Добавление в entries: {data}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка добавления записи", str(e))
            loguru.logger.error(f"Ошибка добавления записи: {e}")

    def update_row(self):
        selected_row = self.table.currentRow()
        if selected_row == -1:
            QMessageBox(self, "Ошибка", "Выберите запись для обновления")
            return

        keys = ["name", "surname", "patronymic", "street", "building", "apartment", "phone"]
        data = {key: field.text() for key, field in zip(keys, self.input_fields)}
        entry_id = self.table.item(selected_row, 0).text()
        data.update({'entry_id':entry_id})

        try:
            self.db.update_data(data)
            self.load_data_from_db()
            QMessageBox.information(self, "Success", "Запись обновлена успешно")
            loguru.logger.info(f"Обновление записи: {data}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка Обновления записи", str(e))
            loguru.logger.error(f"Ошибка обновления записи: {e}")

    def remove_row(self):
        pass