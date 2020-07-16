# -*- coding: utf-8 -*-
# Данная библиотека была портирована из официальной библиотеки к часам LilyGO TTGO T-Watch-2020
# Автор порта: Nikita Selin (Anodev)[https://github.com/OPHoperHPO]
# Автор исходной библиотеки: lewis he
# Лицензия: MIT
# Исходники: https://github.com/lewisxhe/FT5206_Library

FT5206_SLAVE_ADDRESS = 0x38
FT5206_MODE_REG = 0x00
FT5206_TOUCHES_REG = 0x02
FT5206_VENDID_REG = 0xA8
FT5206_CHIPID_REG = 0xA3
FT5206_THRESHHOLD_REG = 0x80
FT5206_POWER_REG = 0x87

FT5206_MONITOR = 0x01
FT5206_SLEEP_IN = 0x03

FT5206_VENDID = 0x11
FT5206_VENDID1 = 0xcd
FT6206_CHIPID = 0x06
FT6236_CHIPID = 0x36
FT6236U_CHIPID = 0x64
FT5206U_CHIPID = 0x64

DEVIDE_MODE = 0x00
TD_STATUS = 0x02
TOUCH1_XH = 0x03
TOUCH1_XL = 0x04
TOUCH1_YH = 0x05
TOUCH1_YL = 0x06

LILYGO_TWATCH_FT62XX = 0x00
LILYGO_TWATCH_CST026 = 0x01

CST026_VENDID = 0x26
FT5X0X_VENDID = 0X56


class FT5206:
    def __init__(self, i2c, address=None):
        self._id = [0] * 2
        self._y = [0] * 2
        self._x = [0] * 2
        self.__touches__ = 0
        self._chip_id = 0xFF
        self.address = address if address else FT5206_SLAVE_ADDRESS

        self.buffer = bytearray(16)
        self.bytebuf = self.buffer

        self.bus = i2c
        self.init_device()

    def init_device(self):
        """
        Инициализирует контроллер
        :return: True
        """
        val = self.read_byte(FT5206_VENDID_REG)
        if self._chip_id == 0xFF:
            if self._chip_id == FT5206_VENDID or self._chip_id == FT5206_VENDID1:
                self._chip_id = val
            else:
                self._chip_id = CST026_VENDID
        return True

    def write_byte(self, reg, val):
        """
        Записывает байт в регистр
        :param reg: Регистр
        :param val: Значение для записи в регистр
        """
        self.bytebuf[0] = val
        self.bus.writeto_mem(self.address, reg, self.bytebuf)

    def read_byte(self, reg, buffer_full=False):
        """
        Читает байт из регистра
        :param reg: Регистр
        :param buffer_full: Вернуть только один байт из буфера или весь буфер
        :return: Буфер или байт
        """
        self.bus.readfrom_mem_into(self.address, reg, self.bytebuf)
        if buffer_full is True:
            return self.bytebuf
        else:
            return self.bytebuf[0]

    def adjust_theshold(self, thresh):
        """
        Порог срабатывания тачскрина
        :param thresh: порог
        :return: True
        """
        self.write_byte(FT5206_THRESHHOLD_REG, thresh)
        return True

    def __read_register__(self):
        data = self.read_byte(DEVIDE_MODE, True)
        self.__touches__ = data[TD_STATUS]
        if (self.__touches__ > 2) or (self.__touches__ == 0):
            self._touches = 0
            return None
        for i in range(0, 2):
            self._x[i] = data[TOUCH1_XH + i * 6] & 0x0F
            self._x[i] <<= 8
            self._x[i] |= data[TOUCH1_XL + i * 6]
            self._y[i] = data[TOUCH1_YH + i * 6] & 0x0F
            self._y[i] <<= 8
            self._y[i] |= data[TOUCH1_YL + i * 6]
            self._id[i] = data[TOUCH1_YH + i * 6] >> 4
        return None

    def get_point(self, num=1):
        """
        Получает позицию, где был затронут тачскрин
        :param num: номер нажатия. Максимум 2.
        :return: Кортеж с координатами x, y
        """
        self.__read_register__()
        if (self.__touches__ == 0) or (num > 2) or num < 1:
            return 0, 0
        else:
            return self._x[num - 1], self._y[num - 1]

    def get_touch(self, x, y):
        """
        Определяет было ли произведено нажатие в конкретных координатах
        :param x: Координата x
        :param y: Координата y
        :return: Bool
        """
        if self.touched() == 0:
            return False
        coords = self.get_point()
        if coords == (x, y):
            return True
        else:
            return False

    def touched(self):
        """
        Определяет кол-во одновременно зафиксированных нажатий.
        :return: Число одновременно зафиксированных нажатий. Максимум 2.
        """
        val = self.read_byte(FT5206_TOUCHES_REG)
        if val > 2:
            return 0
        else:
            return val

    def enter_sleep_mode(self):
        """
        Отправить тачскрин в спящий режим
        :return: True
        """
        self.write_byte(FT5206_POWER_REG, FT5206_SLEEP_IN)
        return True

    def enter_monitor_mode(self):
        """
        Включить режим мониторинга тачскрина
        :return:
        """
        self.write_byte(FT5206_POWER_REG, FT5206_MONITOR)
        return True

    def get_type(self):
        """
        Номер контроллера
        :return:
        """
        return self._chip_id
