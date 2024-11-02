import esphome.codegen as cg
import esphome.config_validation as cv
#from esphome.components import i2c, sensor, sensirion_common
from esphome.components import uart, sensor
from esphome.const import (
    CONF_ID,
    CONF_TEMPERATURE,
    CONF_HUMIDITY,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
    UNIT_PERCENT,
    ICON_THERMOMETER,
    ICON_WATER_PERCENT,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_HUMIDITY,
)

#AQ100 sensor script
DEPENDENCIES = ["uart"]

aq100_ns = cg.esphome_ns.namespace("aq100")

AQ100Component = aq100_ns.class_(
    "AQ100Component", cg.PollingComponent, uart.UARTDevice
)

CONF_PRECISION = "precision"
SHT4XPRECISION = aq100_ns.enum("SHT4XPRECISION")
PRECISION_OPTIONS = {
    "High": SHT4XPRECISION.SHT4X_PRECISION_HIGH,
    "Med": SHT4XPRECISION.SHT4X_PRECISION_MED,
    "Low": SHT4XPRECISION.SHT4X_PRECISION_LOW,
}

CONF_HEATER_POWER = "heater_power"
SHT4XHEATERPOWER = aq100_ns.enum("SHT4XHEATERPOWER")
HEATER_POWER_OPTIONS = {
    "High": SHT4XHEATERPOWER.SHT4X_HEATERPOWER_HIGH,
    "Med": SHT4XHEATERPOWER.SHT4X_HEATERPOWER_MED,
    "Low": SHT4XHEATERPOWER.SHT4X_HEATERPOWER_LOW,
}

CONF_HEATER_TIME = "heater_time"
SHT4XHEATERTIME = aq100_ns.enum("SHT4XHEATERTIME")
HEATER_TIME_OPTIONS = {
    "Long": SHT4XHEATERTIME.SHT4X_HEATERTIME_LONG,
    "Short": SHT4XHEATERTIME.SHT4X_HEATERTIME_SHORT,
}

CONF_HEATER_MAX_DUTY = "heater_max_duty"

CONFIG_SCHEMA = (
    cv.Schema(
        {
            cv.GenerateID(): cv.declare_id(AQ100Component),
            cv.Optional(CONF_TEMPERATURE): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                accuracy_decimals=2,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_HUMIDITY): sensor.sensor_schema(
                unit_of_measurement=UNIT_PERCENT,
                icon=ICON_WATER_PERCENT,
                accuracy_decimals=2,
                device_class=DEVICE_CLASS_HUMIDITY,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_PRECISION, default="High"): cv.enum(PRECISION_OPTIONS),
            cv.Optional(CONF_HEATER_POWER, default="High"): cv.enum(
                HEATER_POWER_OPTIONS
            ),
            cv.Optional(CONF_HEATER_TIME, default="Long"): cv.enum(HEATER_TIME_OPTIONS),
            cv.Optional(CONF_HEATER_MAX_DUTY, default=0.0): cv.float_range(
                min=0.0, max=0.05
            ),
        }
    )
    .extend(cv.polling_component_schema("60s"))
    #.extend(i2c.i2c_device_schema(0x44))
    .extend(uart.UART_DEVICE_SCHEMA)
)

#TYPES = {
#    CONF_TEMPERATURE: "set_temperature_sensor",
#    CONF_HUMIDITY: "set_humidity_sensor",
#}


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    #await i2c.register_i2c_device(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_precision_value(config[CONF_PRECISION]))
    cg.add(var.set_heater_power_value(config[CONF_HEATER_POWER]))
    cg.add(var.set_heater_time_value(config[CONF_HEATER_TIME]))
    cg.add(var.set_heater_duty_value(config[CONF_HEATER_MAX_DUTY]))

    #for key, funcName in TYPES.items():
    #    if key in config:
    #        sens = await sensor.new_sensor(config[key])
    #        cg.add(getattr(var, funcName)(sens))

    if CONF_TEMPERATURE in config:
        sens = await sensor.new_sensor(config[CONF_TEMPERATURE])
        cg.add(var.set_temp_sensor(sens))

    if CONF_HUMIDITY in config:
        sens = await sensor.new_sensor(config[CONF_HUMIDITY])
        cg.add(var.set_humidity_sensor(sens))