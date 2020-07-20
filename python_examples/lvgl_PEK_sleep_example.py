import lvgl as lv
import machine

import ttgo


def axp_callback(pin):
    power.clearIRQ()
    print("PEK was pressed! Go to sleep!!!!")
    watch.tft.backlight_fade(0)
    watch.tft.display_sleep()
    watch.power_off()
    power.setPowerOutPut(ttgo.axp202.AXP202_LDO2, False)
    rtc.wake_on_ext1((35,), 0)
    power.clearIRQ()
    machine.deepsleep()


# Init watch
watch = ttgo.TTGO()

power = watch.pmu
tft = watch.tft

rtc = machine.RTC()  # Init micropython RTC module

# Init lvgl
lv.init()
watch.lvgl_begin()

# Init interface
scr = lv.obj()
win = lv.win(scr)
win.set_title("PowerKey Sleep Example")
text_label = lv.label(win)
text_label.set_text("Wait for the PEKKey\n interrupt to come...")
lv.scr_load(scr)

# Init irq
watch.pmu_attach_interrupt(axp_callback)
power.enableIRQ(ttgo.axp202.AXP202_PEK_SHORTPRESS_IRQ, True)
power.clearIRQ()

# Enable backlight
watch.tft.backlight_fade(100)
