//
// This module will take care of advancing tick count and scheduling async event for lvgl on ESP32.
// It should be imported after lvgl module is imported.
//

#include "py/obj.h"
#include "py/runtime.h"
#include "libs/lvgl/lv_binding/lvgl/lvgl.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_freertos_hooks.h"
#include "esp_log.h"

static const char TAG[] = "[LVGL]";

STATIC mp_obj_t mp_lv_task_handler(mp_obj_t arg)
{
    lv_task_handler();
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_1(mp_lv_task_handler_obj, mp_lv_task_handler);


static void lv_task(void* param)
{
    while(1)
    {
        vTaskDelay(5);
        mp_sched_schedule((mp_obj_t)&mp_lv_task_handler_obj, mp_const_none, NULL);
    }
}



static void lv_tick_task(void)
{
    lv_tick_inc(portTICK_RATE_MS);
}

static TaskHandle_t lvglTaskHandle;
STATIC mp_obj_t mp_init_lvesp32()
{
    BaseType_t xReturned;

    lv_init();

    esp_register_freertos_tick_hook(lv_tick_task);

    xReturned = xTaskCreate(lv_task, "LVGL Task", 4096, NULL, 5, &lvglTaskHandle);
    if (xReturned != pdPASS){
        vTaskDelete(lvglTaskHandle);
        ESP_LOGE(TAG, "Failed creating LVGL task!");
    }
    return mp_const_none;
}

STATIC MP_DEFINE_CONST_FUN_OBJ_0(mp_init_lvesp32_obj, mp_init_lvesp32);


STATIC const mp_rom_map_elem_t lvesp32_globals_table[] = {
        { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_lvesp32) },
        { MP_ROM_QSTR(MP_QSTR___init__), MP_ROM_PTR(&mp_init_lvesp32_obj) },
};

STATIC MP_DEFINE_CONST_DICT (
    mp_module_lvesp32_globals,
    lvesp32_globals_table
);

const mp_obj_module_t mp_module_lvesp32 = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&mp_module_lvesp32_globals
};

