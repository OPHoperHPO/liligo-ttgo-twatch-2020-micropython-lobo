# -*- coding: utf-8 -*-
# Порт официальной библиотеки ttgo для часов LilyGo TTGO T-Watch 2020.
# Автор: Nikita Selin (Anodev)[https://github.com/OPHoperHPO]
import display
from machine import Pin, I2C
from pcf8563 import PCF8563
import bma423 as BMA423
from ft5206 import FT5206
import axp202 as AXP202



class TTGO:
    def __init__(self):
        self.hwconfig = HardwareConfig()
        self.pmu = self.pmu
        self.rtc = self.__init_rtc__()
        self.tft = self.__init_display__()
        self.bma = self.__init_bma__()
        self.touch = self.__init_touch__()


    def __init_touch__(self):
        config = self.hwconfig.TouchScreen.Pins
        touch = FT5206(sda=config.sda, scl=config.scl, intr=config.interrupt)
        return touch

    def __init_bma__(self):
        i2c = I2C(scl=self.hwconfig.Accelerometer.Pins.scl,
                  sda=self.hwconfig.Accelerometer.Pins.sda,
                  speed=400000)
        BMA423.init(i2c)
        return BMA423

    def __init_rtc__(self):
        i2c = I2C(scl=self.hwconfig.RTC.Pins.scl, sda=self.hwconfig.RTC.Pins.sda)
        return PCF8563(i2c)


    def __init_display__(self):
        return Display(self.hwconfig.Display, self.pmu)


class Display:
    """Display wrapper"""

    def __init__(self, disp_config, pmu):
        """Inits display"""
        # Init display
        tft = display.TFT()
        tft.init(tft.ST7789, mosi=disp_config.Pins.mosi, miso=disp_config.Pins.miso,
                 clk=disp_config.Pins.clk, cs=disp_config.Pins.cs, dc=disp_config.Pins.dc,
                 rst_pin=disp_config.Pins.rst, backl_pin=disp_config.Pins.bl,
                 splash=False, backl_on=1,
                 width=240, height=320)
        self.tft = tft
        self.pmu = pmu

        self.tft.tft_writecmd(0x21)  # Invert colors
        self.set_backlight_level(0)  # Turn backlight off
        self.backlight_level = 0
        self.backlight(1)  # Enable power on backlight
        self.tft.setwin(0, 80, 240, 320)  # Resize window

    def backlight_fade(self, val=100):
        if val > self.backlight_level:
            data = 0
            for i in range(self.backlight_level, val):
                data = i
                self.set_backlight_level(i)
            self.backlight_level = data
            return True
        elif val < self.backlight_level:
            data = 0
            for i in reversed(range(val, self.backlight_level)):
                data = i
                self.set_backlight_level(i)
            self.backlight_level = data
            return True

    def clear(self):
        self.tft.clear()

    def switch_scene(self):
        level = self.backlight_level
        self.backlight_fade(0)
        self.clear()
        self.backlight_fade(level)

    def set_backlight_level(self, percent):
        if 0 <= percent <= 100:
            voltage = 800 * percent / 100
            self.pmu.set_lcd_backlight_voltage(2400 + voltage)

    def backlight(self, val):
        self.tft.backlight(val)
        self.pmu.turn_lcd_backlight(val)

    def print_text(self, x, y, text: str, color: tuple = ()):
        if not color:
            self.tft.text(x, y, text)
        else:
            self.tft.text(x, y, text, self.__rgb_tuple2rgb_int__(color))

    def __rgb_tuple2rgb_int__(self, rgb_tuple):
        return rgb_tuple[0] << 16 | rgb_tuple[1] << 8 | rgb_tuple[2]






class HardwareConfig:
    """Конфиг для LilyGO T-Watch-2020"""

    class Display:
        """
        Класс дисплея
        Контроллер: ST7789V
        Разрешение: 240x240
        """
        width = 240
        height = 240
        window_size_correction = (0, 80, 240, 320)
        class Pins:
            """Класс пинов для подключения"""
            miso = 0
            mosi = 19
            clk = 18
            cs = 5
            dc = 27
            rst = 0
            bl = 12

    class TouchScreen:
        """
        Класс тачскрина
        Контроллер: FT6236U
        """

        class Pins:
            """Класс пинов для подключения"""
            sda = 23
            scl = 32
            interrupt = 38

    class Accelerometer:
        """
        Класс акселирометра
        Контроллер: BMA423
        """

        class Pins:
            """Класс пинов для подключения"""
            sda = 21
            scl = 22
            interrupt = 39

    class RTC:
        """
        Класс RTC модуля
        Контроллер: PCF8563
        """

        class Pins:
            """Класс пинов для подключения"""
            sda = 21
            scl = 22
            interrupt = 37

    class PMU:
        """
        Класс менеджера питания часов
        Контроллер: AXP202
        """

        class Pins:
            """Класс пинов для подключения"""
            sda = 21
            scl = 22
            interrupt = 35

    class Motor:
        """
        Класс вибромотора
        """

        class Pins:
            """Класс пинов для подключения"""
            pin = 4

    class IR:
        """
        Класс инфракрасного датчика
        """

        class Pins:
            """Класс пинов для подключения"""
            pin = 13

    class Audio:
        """
        Класс аудиоусилителя
        Контроллер: MAX98357A
        """

        class Pins:
            """Класс пинов для подключения"""
            ws = 25
            bck = 26
            dout = 33
