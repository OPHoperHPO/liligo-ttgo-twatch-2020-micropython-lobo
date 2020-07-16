import time
import ttgo
import lvgl as lv
import machine

def axp_callback(pin):
    power.clearIRQ()
    for i in reversed(range(5, 0)):
        text_label.set_text("Go to sleep after {} seconds".format(i))
        time.sleep(1)
        tft.clear()
    text_label.set_text("Sleep now...")
    time.sleep(2)
    watch.tft.backlight_fade(0)
    watch.tft.display_sleep()
    watch.power_off()
    power.setPowerOutPut(ttgo.axp202.AXP202_LDO2, False)
    rtc.wake_on_ext1((35,), 0)
    power.clearIRQ()
    machine.deepsleep()

rtc = machine.RTC()
watch = ttgo.TTGO()

watch.lvgl_begin()

scr = lv.obj()
win = lv.win(scr)
win.set_title("PowerKey Sleep Example")
text_label = lv.label(win)
text_label.set_text("Wait for the PEKKey interrupt to come...")

watch.tft.backlight_fade(100)

tft = watch.tft.tft
power = watch.pmu

watch.pmu_attach_interrupt(axp_callback)
power.enableIRQ(ttgo.axp202.AXP202_PEK_SHORTPRESS_IRQ, True)

lv.scr_load(scr)

while True:
    power.clearIRQ()

