import sys, os, configparser
from decimal import Decimal

from main import Ui_MainWindow
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableWidgetItem


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Загрузка параметров
        self.load_param()

        # Заполнение comboBox-ов
        self.comboBox_load(0)  # средства калибровки
        self.comboBox_load(1)  # выходные величины
        self.comboBox_load(2)  # сдал
        self.comboBox_load(3)  # принял

    # Валидация полей Вход, Выход, Шкала ПВИ параметров прибора
        self.ui.lineEdit_in_start_value.setValidator(self.validat_param())
        self.ui.lineEdit_in_end_value.setValidator(self.validat_param())
        self.ui.lineEdit_out_start_value.setValidator(self.validat_param())
        self.ui.lineEdit_out_end_value.setValidator(self.validat_param())

        self.ui.lineEdit_pvi_scale_start.setValidator(self.validat_param())
        self.ui.lineEdit_pvi_scale_start.setValidator(self.validat_param())

        # Валиддация показаний Выход ИРТ, Выход ПВИ
        self.ui.lineEdit_out_irt_value_5.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_irt_value_25.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_irt_value_50.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_irt_value_75.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_irt_value_95.setValidator(self.validat_in_out())

        self.ui.lineEdit_out_pvi_value_5.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_pvi_value_25.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_pvi_value_50.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_pvi_value_75.setValidator(self.validat_in_out())
        self.ui.lineEdit_out_pvi_value_95.setValidator(self.validat_in_out())

        # Дата сегодня
        self.ui.dateEdit_date_calibration.setDate(QtCore.QDate.currentDate())

        # Валидация полей Выход 24В
        self.ui.lineEdit_out_24_value_0.setValidator(self.valdat_24())
        self.ui.lineEdit_out_24_value_820.setValidator(self.valdat_24())

        # Группа ПВИ(чекбокс)
        self.ui.groupBox_out_pvi.setEnabled(False)
        self.ui.checkBox_pvi.stateChanged.connect(lambda check=self.ui.checkBox_pvi.isChecked(): self.select_pvi(check))


        # Установка входных значений выходов ИРТ
        self.ui.lineEdit_in_start_value.textChanged.connect(self.out_irt_in)
        self.ui.lineEdit_in_end_value.textChanged.connect(self.out_irt_in)

        # Установка выходных значений выходов ИРТ
        self.ui.lineEdit_out_start_value.textChanged.connect(self.out_irt_out)
        self.ui.lineEdit_out_end_value.textChanged.connect(self.out_irt_out)

        # Установка входных значений выходов ПВИ
        self.ui.lineEdit_pvi_scale_start.textChanged.connect(self.out_pvi_in)
        self.ui.lineEdit_pvi_scale_end.textChanged.connect(self.out_pvi_in)

        # Установка выходных значений выходов ПВИ и R ПВИ
        self.ui.comboBox_pvi_out.activated.connect(self.out_pvi_out)

        # Установка допуска ПВИ
        self.ui.lineEdit_out_start_value.textChanged.connect(self.acceptance_irt)
        self.ui.lineEdit_out_end_value.textChanged.connect(self.acceptance_irt)

        # Установка параметров входа
        self.ui.comboBox_in_signal_type.activated.connect(self.parametr_in_signal)

        # Сохранение настроек
        self.ui.pushButton_save_custom.clicked.connect(self.save_param)

        # Сохранение файла конфигурации прибора
        self.ui.pushButton_save_config.clicked.connect(self.save_config_file)
        self.ui.action_save_config.triggered.connect(self.save_config_file)

        # Загрузка файла конфигурации прибора
        self.ui.action_load_config.triggered.connect(self.load_config_file)

        # О программе
        self.ui.action_about.triggered.connect(self.about)

        # Выход из программы
        self.ui.action_exit.triggered.connect(self.exit)

    def parametr_in_signal(self):
        """ Устанавливает параметры прибора(входные значения) """
        sensor_type = {
            "ТП-ХК": (-50, 600),
            "ТП-ХА": (-50, 1300),
            "0-5 мА": (0, 5),
            "0-20 мА": (0, 20),
            "4-20 мА": (4, 20),
            "ТСМ-50М": (-50, 200),
            "ТСМ-100М": (-50, 200),
            "ТСМ-50П": (-50, 600),
            "ТСМ-100П": (-50, 600),
        }

        sensor_type_key = self.ui.comboBox_in_signal_type.currentText()
        if sensor_type_key in sensor_type.keys():
            self.ui.lineEdit_in_start_value.setText(str(sensor_type.get(sensor_type_key)[0]))
            self.ui.lineEdit_in_end_value.setText(str(sensor_type.get(sensor_type_key)[1]))

            if "Т" in sensor_type_key:
                self.ui.lineEdit_out_start_value.setText(str(sensor_type.get(sensor_type_key)[0]))
                self.ui.lineEdit_out_end_value.setText(str(sensor_type.get(sensor_type_key)[1]))
            else:
                self.ui.lineEdit_out_start_value.setText("")
                self.ui.lineEdit_out_end_value.setText("")

        else:
            self.ui.lineEdit_in_start_value.setText("")
            self.ui.lineEdit_in_end_value.setText("")

            self.ui.lineEdit_out_start_value.setText("")
            self.ui.lineEdit_out_end_value.setText("")

        # Допуск ИРТ
        self.acceptance_irt()

    def validat_param(self):
        """ Валидация полей Вход, Выход, Шкала ПВИ параметров прибора """
        return QtGui.QRegExpValidator(QtCore.QRegExp("^[+-]?\d{,6}(?:[\.,]\d{,3})?$"))

    def validat_in_out(self):
        """ Валиддация показаний Выход ИРТ, Выход ПВИ """
        return QtGui.QRegExpValidator(QtCore.QRegExp("^[+-]?\d{,5}(?:[\.,]\d{,3})?$"))

    def valdat_24(self):
        """ Валидация полей Выход 24В """
        return QtGui.QRegExpValidator(QtCore.QRegExp("^[+-]?\d{,2}(?:[\.,]\d{,3})?$"))

    def comboBox_load(self, col=0):
        """ Заполнение ComboBox из tableWidget """
        _translate = QtCore.QCoreApplication.translate

        table = self.ui.tableWidget_param
        container = ['']

        for row in range(0, table.rowCount()):
            try:
                device = table.item(row, col).text()
                container.append(device)
            except:
                pass

        if col == 0:
            for n, i in enumerate(container):
                self.ui.comboBox_calibr_name.addItem("")
                self.ui.comboBox_calibr_name.setItemText(n, _translate("MainWindow", i))

        elif col == 1:
            for n, i in enumerate(container):
                self.ui.comboBox_out_signal_type.addItem("")
                self.ui.comboBox_out_signal_type.setItemText(n, _translate("MainWindow", i))

        elif col == 2:
            for n, i in enumerate(container):
                self.ui.comboBox_passed.addItem("")
                self.ui.comboBox_passed.setItemText(n, _translate("MainWindow", i))

        elif col == 3:
            for n, i in enumerate(container):
                self.ui.comboBox_adopted.addItem("")
                self.ui.comboBox_adopted.setItemText(n, _translate("MainWindow", i))

        container.clear()

    def select_pvi(self, pvi_on):
        """ Включение группы ПВИ """
        self.ui.groupBox_out_pvi.setEnabled(pvi_on)
        if pvi_on == QtCore.Qt.Checked:
            self.ui.label_pvi_scale.setEnabled(True)
            self.ui.lineEdit_pvi_scale_start.setEnabled(True)
            self.ui.lineEdit_pvi_scale_end.setEnabled(True)
            self.ui.label_pvi_out.setEnabled(True)
            self.ui.comboBox_pvi_out.setEnabled(True)
            self.ui.label_pvi_out_r.setEnabled(True)
        else:
            self.ui.label_pvi_scale.setEnabled(False)
            self.ui.lineEdit_pvi_scale_start.setEnabled(False)
            self.ui.lineEdit_pvi_scale_end.setEnabled(False)
            self.ui.label_pvi_out.setEnabled(False)
            self.ui.comboBox_pvi_out.setEnabled(False)
            self.ui.label_pvi_out_r.setEnabled(False)

    def is_number(self, num):
        """ Преобразует в Decimal """
        try:
            num = num.replace(',', '.')
            if float(num) or float(num) == 0:
                return Decimal(num)
        except:
            pass

    def out_irt_in(self):
        """ Расчет требуемых входных """
        values = ['']
        try:
            # Установка входных
            in_start = float(self.ui.lineEdit_in_start_value.text().replace(',', '.'))
            in_end = float(self.ui.lineEdit_in_end_value.text().replace(',', '.'))

            for i in (0.05, 0.25, 0.5, 0.75, 0.95):
                values.append(str(round((float(in_end) - float(in_start)) * i + float(in_start), 3)))

            self.ui.lineEdit_out_irt_in_5.setText(values[1])
            self.ui.lineEdit_out_irt_in_25.setText(values[2])
            self.ui.lineEdit_out_irt_in_50.setText(values[3])
            self.ui.lineEdit_out_irt_in_75.setText(values[4])
            self.ui.lineEdit_out_irt_in_95.setText(values[5])
        except:
            self.ui.lineEdit_out_irt_in_5.setText(values[0])
            self.ui.lineEdit_out_irt_in_25.setText(values[0])
            self.ui.lineEdit_out_irt_in_50.setText(values[0])
            self.ui.lineEdit_out_irt_in_75.setText(values[0])
            self.ui.lineEdit_out_irt_in_95.setText(values[0])

    def out_irt_out(self):
        """ Расчет требуемых выходных """
        values = ['']
        try:
            # Установка выходных
            in_start = float(self.ui.lineEdit_out_start_value.text().replace(',', '.'))
            in_end = float(self.ui.lineEdit_out_end_value.text().replace(',', '.'))

            for i in (0.05, 0.25, 0.5, 0.75, 0.95):
                values.append(str(round((float(in_end) - float(in_start)) * i + float(in_start), 3)))

            self.ui.lineEdit_out_irt_output_5.setText(values[1])
            self.ui.lineEdit_out_irt_output_25.setText(values[2])
            self.ui.lineEdit_out_irt_output_50.setText(values[3])
            self.ui.lineEdit_out_irt_output_75.setText(values[4])
            self.ui.lineEdit_out_irt_output_95.setText(values[5])
        except:
            self.ui.lineEdit_out_irt_output_5.setText(values[0])
            self.ui.lineEdit_out_irt_output_25.setText(values[0])
            self.ui.lineEdit_out_irt_output_50.setText(values[0])
            self.ui.lineEdit_out_irt_output_75.setText(values[0])
            self.ui.lineEdit_out_irt_output_95.setText(values[0])


    def out_pvi_in(self):
        """ Расчет требуемых входных ПВИ"""
        values = ['']
        try:
            in_start = float(self.ui.lineEdit_pvi_scale_start.text().replace(',', '.'))
            in_end = float(self.ui.lineEdit_pvi_scale_end.text().replace(',', '.'))

            for i in (0.05, 0.25, 0.5, 0.75, 0.95):
                values.append(str((in_end - in_start) * i + in_start))

            self.ui.lineEdit_out_pvi_in_5.setText(values[1])
            self.ui.lineEdit_out_pvi_in_25.setText(values[2])
            self.ui.lineEdit_out_pvi_in_50.setText(values[3])
            self.ui.lineEdit_out_pvi_in_75.setText(values[4])
            self.ui.lineEdit_out_pvi_in_95.setText(values[5])
        except:
            self.ui.lineEdit_out_pvi_in_5.setText(values[0])
            self.ui.lineEdit_out_pvi_in_25.setText(values[0])
            self.ui.lineEdit_out_pvi_in_50.setText(values[0])
            self.ui.lineEdit_out_pvi_in_75.setText(values[0])
            self.ui.lineEdit_out_pvi_in_95.setText(values[0])

    def out_pvi_out(self):
        """ Расчет требуемых выходных ПВИ"""
        values = ['']
        try:
            type_out = self.ui.comboBox_pvi_out.currentText().split('-')

            in_start = int(type_out[0])
            in_end = int(type_out[1])

            print(in_start, in_end)
            for i in (0.05, 0.25, 0.5, 0.75, 0.95):
                values.append(str((in_end - in_start) * i + in_start))

            print(values)
            self.ui.lineEdit_out_pvi_output_5.setText(values[1])
            self.ui.lineEdit_out_pvi_output_25.setText(values[2])
            self.ui.lineEdit_out_pvi_output_50.setText(values[3])
            self.ui.lineEdit_out_pvi_output_75.setText(values[4])
            self.ui.lineEdit_out_pvi_output_95.setText(values[5])
        except:
            self.ui.lineEdit_out_pvi_output_5.setText(values[0])
            self.ui.lineEdit_out_pvi_output_25.setText(values[0])
            self.ui.lineEdit_out_pvi_output_50.setText(values[0])
            self.ui.lineEdit_out_pvi_output_75.setText(values[0])
            self.ui.lineEdit_out_pvi_output_95.setText(values[0])

        # R ПВИ
        r_pvi = {
            "0-5": "1.8 кОм",
            "0-20": "470 Ом",
            "4-20": "470 Ом"
        }

        r_pvi_key = self.ui.comboBox_pvi_out.currentText()
        if r_pvi_key in r_pvi.keys():
            self.ui.label_pvi_out_r.setText(f"R={str(r_pvi[r_pvi_key])}±5%")

    def acceptance_irt(self):
        """ Устанавливает допуск ИРТ """
        out_start = self.is_number(self.ui.lineEdit_out_start_value.text())
        out_end = self.is_number(self.ui.lineEdit_out_end_value.text())

        one_unit_last_number = 0
        try:
            range_scale = str(out_end - out_start)

            dig = abs(range_scale.find('.') - len(range_scale)) - 1 if '.' in range_scale else 0
            if dig == 0:
                one_unit_last_number = 1
            if dig == 1:
                one_unit_last_number = 0.1
            if dig == 2:
                one_unit_last_number = 0.01
            if dig == 3:
                one_unit_last_number = 0.001

            # одна единица последнего разряда, выраженная в процентах от диапазона измерений
            one_unit_last_number = abs(one_unit_last_number / float(range_scale) * 100)
        except:
            pass

        _K_THRM, _K_RESIST = 0.5, 0.2 # допуски(табличные данные), не трогать

        in_signal_type = self.ui.comboBox_in_signal_type.currentText().lower()
        if 'м' in in_signal_type:
            in_signal_text = f"Допуск ±({_K_RESIST} + {one_unit_last_number:.3f})"
        elif 'тп' in in_signal_type:
            in_signal_text = f"Допуск ±({_K_THRM} + {one_unit_last_number:.3f})"
        else:
            in_signal_text = f"Допуск ±(0,0 + *)"

        self.ui.label_acceptance_error_irt.setText(in_signal_text)

    def acceptance_error_pvi(self):
        """ Рассчет допусков ПВИ """
        pass

    def load_param(self):
        """ Загрузка параметров """
        try:
            config = configparser.ConfigParser()
            config.read("parameters.ini", encoding="utf-8")
            table = self.ui.tableWidget_param

            for column in range(0, table.columnCount()):
                column_name = table.horizontalHeaderItem(column).text()
                param = config.items(column_name)

                for row in range(0, len(param)):
                    table.setItem(row, column, QTableWidgetItem(param[row][1]))
        except Exception as exeption:
            QtWidgets.QMessageBox.critical(self, "Ошибка",
                                           f"Не удалось загрузить параметры из файла <parameters.ini>. Ошибка - {type(exeption).__name__}",
                                           QtWidgets.QMessageBox.Ok)

    def save_param(self):
        """ Сохранение параметров """
        table = self.ui.tableWidget_param
        config = configparser.ConfigParser()

        for column in range(0, table.columnCount()):
            column_name = table.horizontalHeaderItem(column).text()
            config.add_section(column_name)

            for row in range(0, table.rowCount()):
                try:
                    value = table.item(row, column).text()
                    config.set(column_name, str(row), value)
                except:
                    pass

        try:
            with open("parameters.ini", "w", "utf8") as config_file:
                config.write(config_file)
            QtWidgets.QMessageBox.information(self, "Параметры сохранены",
                                              "Необходимо перезагрузить программу для обновления параметров.",
                                              QtWidgets.QMessageBox.Ok)
        except Exception as exeption:
            QtWidgets.QMessageBox.critical(self, "Ошибка записи",
                                           f"Не удалось сохранить параметры. Ошибка - {type(exeption).__name__}",
                                           QtWidgets.QMessageBox.Ok)

    def save_config_file(self):
        """ Сохраняет файл конфигурации прибора """
        file_path = "configurations"
        file_name = self.ui.lineEdit_parametr_position.text()

        config = configparser.ConfigParser()
        config.add_section("Средство калибровки")
        config.set("Средство калибровки", "Калибратор", self.ui.comboBox_calibr_name.currentText())

        config.add_section("Параметры прибора")
        config.set("Параметры прибора", "Тип", self.ui.comboBox_parametr_type.currentText())
        config.set("Параметры прибора", "Номер", self.ui.lineEdit_parametr_number.text())
        config.set("Параметры прибора", "Год выпуска", self.ui.comboBox_parametr_year.currentText())
        config.set("Параметры прибора", "Позиция", self.ui.lineEdit_parametr_position.text())
        config.set("Параметры прибора", "Тип входа", self.ui.comboBox_in_signal_type.currentText())
        config.set("Параметры прибора", "Вход начало шкалы", self.ui.lineEdit_in_start_value.text())
        config.set("Параметры прибора", "Вход конец шкалы", self.ui.lineEdit_in_end_value.text())
        config.set("Параметры прибора", "Тип выхода", self.ui.comboBox_out_signal_type.currentText())
        config.set("Параметры прибора", "Выход начало шкалы", self.ui.lineEdit_out_start_value.text())
        config.set("Параметры прибора", "Выход конец шкалы", self.ui.lineEdit_out_end_value.text())
        config.set("Параметры прибора", "Наличие ПВИ", str(self.ui.checkBox_pvi.isChecked()))
        config.set("Параметры прибора", "ПВИ начало шкалы", self.ui.lineEdit_pvi_scale_start.text())
        config.set("Параметры прибора", "ПВИ конец шкалы", self.ui.lineEdit_pvi_scale_end.text())
        config.set("Параметры прибора", "ПВИ тип выхода", self.ui.comboBox_pvi_out.currentText())

        config.add_section("Выход ИРТ")
        config.set("Выход ИРТ", "Показания 5", self.ui.lineEdit_out_irt_value_5.text())
        config.set("Выход ИРТ", "Показания 25", self.ui.lineEdit_out_irt_value_25.text())
        config.set("Выход ИРТ", "Показания 50", self.ui.lineEdit_out_irt_value_50.text())
        config.set("Выход ИРТ", "Показания 75", self.ui.lineEdit_out_irt_value_75.text())
        config.set("Выход ИРТ", "Показания 95", self.ui.lineEdit_out_irt_value_95.text())


        config.add_section("Выход 24В")
        config.set("Выход 24В", "Выход R0", self.ui.lineEdit_out_24_value_0.text())
        config.set("Выход 24В", "Выход R820", self.ui.lineEdit_out_24_value_820.text())

        config.add_section("Выход ПВИ")
        config.set("Выход ПВИ", "Показания 5", self.ui.lineEdit_out_pvi_value_5.text())
        config.set("Выход ПВИ", "Показания 25", self.ui.lineEdit_out_pvi_value_25.text())
        config.set("Выход ПВИ", "Показания 50", self.ui.lineEdit_out_pvi_value_50.text())
        config.set("Выход ПВИ", "Показания 75", self.ui.lineEdit_out_pvi_value_75.text())
        config.set("Выход ПВИ", "Показания 95", self.ui.lineEdit_out_pvi_value_95.text())

        config.set("Выход ПВИ", "Выход 5", self.ui.lineEdit_out_pvi_output_5.text())
        config.set("Выход ПВИ", "Выход 25", self.ui.lineEdit_out_pvi_output_25.text())
        config.set("Выход ПВИ", "Выход 50", self.ui.lineEdit_out_pvi_output_50.text())
        config.set("Выход ПВИ", "Выход 75", self.ui.lineEdit_out_pvi_output_75.text())
        config.set("Выход ПВИ", "Выход 95", self.ui.lineEdit_out_pvi_output_95.text())

        config.add_section("Сдал/Принял/Дата")
        config.set("Сдал/Принял/Дата", "Сдал", self.ui.comboBox_passed.currentText())
        config.set("Сдал/Принял/Дата", "Принял", self.ui.comboBox_adopted.currentText())
        config.set("Сдал/Принял/Дата", "дата калибровки(ДД.ММ.ГГГГ)",
                   self.ui.dateEdit_date_calibration.dateTime().toString('dd.MM.yyyy'))

        try:
            if not os.path.isdir(file_path):
                os.mkdir(file_path)

            with open(f"{file_path}/{file_name}.clbr59", "w", encoding="UTF-8") as config_file:
                config.write(config_file)

            QtWidgets.QMessageBox.information(self, "Сохранено",
                                              f"Конфигурация {file_name} успешно сохранена", QtWidgets.QMessageBox.Ok)

        except Exception as exeption:
            QtWidgets.QMessageBox.critical(self, "Ошибка записи",
                                           f"Не удалось сохранить параметры. Ошибка - {type(exeption).__name__}",
                                           QtWidgets.QMessageBox.Ok)

    def load_config_file(self):
        """ Загружает пользовательский файл конфигурации """
        path = f"{os.path.abspath(os.curdir)}\configurations"
        file = QtWidgets.QFileDialog.getOpenFileName(parent=application,
                                                     caption="Загрузить файл",
                                                     directory=path,
                                                     filter="All (*);;clbr59 (*.clbr59)",
                                                     initialFilter="clbr59 (*.clbr59)",)

        config = configparser.ConfigParser()
        config.read(file[0], encoding="UTF-8")

        _translate = QtCore.QCoreApplication.translate

        self.ui.comboBox_calibr_name.setItemText(0, _translate("MainWindow", config.get("Средство калибровки", "калибратор")))

        self.ui.comboBox_parametr_type.setItemText(0, _translate("MainWindow", config.get("Параметры прибора", "тип")))
        self.ui.lineEdit_parametr_number.setText(config.get("Параметры прибора", "номер"))
        self.ui.comboBox_parametr_year.setItemText(0, _translate("MainWindow", config.get("Параметры прибора", "год выпуска")))
        self.ui.lineEdit_parametr_position.setText(config.get("Параметры прибора", "позиция"))
        self.ui.comboBox_in_signal_type.setItemText(0, _translate("MainWindow", config.get("Параметры прибора", "тип входа")))
        self.ui.lineEdit_in_start_value.setText(config.get("Параметры прибора", "вход начало шкалы"))
        self.ui.lineEdit_in_end_value.setText(config.get("Параметры прибора", "вход конец шкалы"))
        self.ui.comboBox_out_signal_type.setItemText(0, _translate("MainWindow", config.get("Параметры прибора", "тип выхода")))
        self.ui.lineEdit_out_start_value.setText(config.get("Параметры прибора", "выход начало шкалы"))
        self.ui.lineEdit_out_end_value.setText(config.get("Параметры прибора", "выход конец шкалы"))
        if config.get("Параметры прибора", "наличие пви") == 'True':
            self.ui.checkBox_pvi.setChecked(True)
        else:
            self.ui.checkBox_pvi.setChecked(False)
        self.ui.lineEdit_pvi_scale_start.setText(config.get("Параметры прибора", "пви начало шкалы"))
        self.ui.lineEdit_pvi_scale_end.setText(config.get("Параметры прибора", "пви конец шкалы"))
        self.ui.comboBox_pvi_out.setItemText(0, _translate("MainWindow", config.get("Параметры прибора", "пви тип выхода")))

        self.ui.lineEdit_out_irt_value_5.setText(config.get("Выход ИРТ", "показания 5"))
        self.ui.lineEdit_out_irt_value_25.setText(config.get("Выход ИРТ", "показания 25"))
        self.ui.lineEdit_out_irt_value_50.setText(config.get("Выход ИРТ", "показания 50"))
        self.ui.lineEdit_out_irt_value_75.setText(config.get("Выход ИРТ", "показания 75"))
        self.ui.lineEdit_out_irt_value_95.setText(config.get("Выход ИРТ", "показания 95"))

        self.ui.lineEdit_out_24_value_0.setText(config.get("Выход 24В", "выход r0"))
        self.ui.lineEdit_out_24_value_820.setText(config.get("Выход 24В", "выход r820"))

        self.ui.lineEdit_out_pvi_value_5.setText(config.get("Выход ПВИ", "показания 5"))
        self.ui.lineEdit_out_pvi_value_25.setText(config.get("Выход ПВИ", "показания 25"))
        self.ui.lineEdit_out_pvi_value_50.setText(config.get("Выход ПВИ", "показания 50"))
        self.ui.lineEdit_out_pvi_value_75.setText(config.get("Выход ПВИ", "показания 75"))
        self.ui.lineEdit_out_pvi_value_95.setText(config.get("Выход ПВИ", "показания 95"))

        self.ui.lineEdit_out_pvi_output_5.setText(config.get("Выход ПВИ", "выход 5"))
        self.ui.lineEdit_out_pvi_output_25.setText(config.get("Выход ПВИ", "выход 25"))
        self.ui.lineEdit_out_pvi_output_50.setText(config.get("Выход ПВИ", "выход 50"))
        self.ui.lineEdit_out_pvi_output_75.setText(config.get("Выход ПВИ", "выход 75"))
        self.ui.lineEdit_out_pvi_output_95.setText(config.get("Выход ПВИ", "выход 95"))

        self.ui.comboBox_passed.setItemText(0, _translate("MainWindow", config.get("Сдал/Принял/Дата", "сдал")))
        self.ui.comboBox_adopted.setItemText(0, _translate("MainWindow", config.get("Сдал/Принял/Дата", "принял")))

        date_c = tuple(map(int, config.get("Сдал/Принял/Дата", "дата калибровки(ДД.ММ.ГГГГ)").split('.')))
        self.ui.dateEdit_date_calibration.setDate(QtCore.QDate(date_c[0], date_c[1], date_c[2]))

    def about(self):
        QtWidgets.QMessageBox.aboutQt(application, title="О программе")

    def exit(self):
        dialog = QtWidgets.QMessageBox.question(application, "Выход из программы",
                                                "Сохранить файл конфигурации прибора?",
                                                buttons=QtWidgets.QMessageBox.Cancel | QtWidgets.QMessageBox.No |
                                                        QtWidgets.QMessageBox.Yes,
                                                defaultButton=QtWidgets.QMessageBox.Yes)
        if dialog == 65536:
            sys.exit(app.exec())
        if dialog == 16384:
            self.save_config_file()
            sys.exit(app.exec())
        if dialog == 4194304:
            pass


app = QtWidgets.QApplication([])
application = Window()
application.setWindowTitle("Создание протокола калибровки ИРТ 5920Н, 5940М")
application.setFixedSize(800, 670)
application.show()

sys.exit(app.exec())
