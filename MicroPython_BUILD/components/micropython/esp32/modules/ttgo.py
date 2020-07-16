# -*- coding: utf-8 -*-
# Порт официальной библиотеки ttgo для часов LilyGo TTGO T-Watch 2020.
# Автор: Nikita Selin (Anodev)[https://github.com/OPHoperHPO]
import display
from ft5206 import FT5206
import bma423 as BMA423
from pcf8563 import PCF8563
import axp202
from machine import Pin, I2C, PWM


class TTGO:
    def __init__(self):
        self.__i2c__ = I2C(scl=22, sda=21, speed=400000)
        self.pmu = axp202.PMU(self.__i2c__)
        self.rtc = PCF8563(self.__i2c__)
        self.tft = self.__init_display__()
        self.bma = self.__init_bma__()
        self.__i2c2__ = I2C(id=1, scl=32, sda=23, speed=400000)
        self.touch = FT5206(self.__i2c2__)

    def __init_bma__(self):
        BMA423.init(self.__i2c__)
        return BMA423

    def __init_display__(self):
        return Display(self.pmu)

    def init_power(self):
        # Change the button boot time to 4 seconds
        self.pmu.setShutdownTime(axp202.AXP_POWER_OFF_TIME_4S)
        # Turn off the charging instructions, there should be no
        self.pmu.setChgLEDMode(axp202.AXP20X_LED_OFF)
        # Turn off external enable
        self.pmu.setPowerOutPut(axp202.AXP202_EXTEN, False)
        # axp202 allows maximum charging current of 1800mA, minimum 300mA
        self.pmu.setChargeControlCur(300)

    def power_off(self):
        self.pmu.setPowerOutPut(axp202.AXP202_EXTEN, False)
        self.pmu.setPowerOutPut(axp202.AXP202_LDO4, False)
        self.pmu.setPowerOutPut(axp202.AXP202_DCDC2, False)
        self.pmu.setPowerOutPut(axp202.AXP202_LDO3, False)
        self.pmu.setPowerOutPut(axp202.AXP202_LDO2, False)


class Display:
    """Display wrapper"""

    def __init__(self, pmu):
        """Inits display"""
        # Init display
        tft = display.TFT()
        tft.init(tft.ST7789, width=240, invrot=3,
                 rot=1, bgr=False, height=240, miso=2, mosi=19, clk=18, cs=5, dc=27,
                 speed=40000000, color_bits=tft.COLOR_BITS16, backl_pin=12, backl_on=1)
        self.tft = tft
        self.pmu = pmu
        self.set_backlight_level(0)  # Turn backlight off
        self.backlight_level = 0
        self.backlight(1)  # Enable power on backlight

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

    def __rgb_tuple2rgb_int__(self, rgb_tuple):
        return rgb_tuple[0] << 16 | rgb_tuple[1] << 8 | rgb_tuple[2]


class Motor:
    def __init__(self):
        self.pwm = PWM(4, freq=1000, duty=0)

    def on(self):
        self.pwm.resume()
        self.pwm.duty(5)

    def off(self):
        self.pwm.duty(0)
        self.pwm.pause()

    def set_strength(self, strength):
        self.pwm.duty(5 * strength / 100)

    def set_freq(self, freq):
        self.pwm.freq(freq)
