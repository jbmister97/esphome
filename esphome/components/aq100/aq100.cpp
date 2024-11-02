#include "aq100.h"
#include "esphome/core/log.h"

namespace esphome {
namespace aq100 {

static const char *const TAG = "aq100";

//static const uint8_t MEASURECOMMANDS[] = {0xFD, 0xF6, 0xE0};
static const char HEATERCMD[] = "%htr%";
static const char GETTEMPCMD[] = "%temp%";
static const char GETHUMCMD[] = "%hum%";

void AQ100Component::start_heater_() {
  ESP_LOGD(TAG, "Heater turning on");
  this->write_str(HEATERCMD);
  this->write_byte(this->heater_command_);
}

void AQ100Component::setup() {
  ESP_LOGCONFIG(TAG, "Setting up aq100...");

  if (this->duty_cycle_ > 0.0) {
    uint32_t heater_interval = (uint32_t) (this->heater_time_ / this->duty_cycle_);
    ESP_LOGD(TAG, "Heater interval: %" PRIu32, heater_interval);

    if (this->heater_power_ == SHT4X_HEATERPOWER_HIGH) {
      if (this->heater_time_ == SHT4X_HEATERTIME_LONG) {
        this->heater_command_ = 0x39;
      } else {
        this->heater_command_ = 0x32;
      }
    } else if (this->heater_power_ == SHT4X_HEATERPOWER_MED) {
      if (this->heater_time_ == SHT4X_HEATERTIME_LONG) {
        this->heater_command_ = 0x2F;
      } else {
        this->heater_command_ = 0x24;
      }
    } else {
      if (this->heater_time_ == SHT4X_HEATERTIME_LONG) {
        this->heater_command_ = 0x1E;
      } else {
        this->heater_command_ = 0x15;
      }
    }
    ESP_LOGD(TAG, "Heater command: %x", this->heater_command_);

    this->set_interval(heater_interval, std::bind(&AQ100Component::start_heater_, this));
  }
}

//void SHT4XComponent::dump_config() { LOG_I2C_DEVICE(this); }
void AQ100Component::dump_config() { ESP_LOGCONFIG(TAG, "AQ100 dump config..."); }

void AQ100Component::update() {
  // Send temperature read command
  this->write_str(GETTEMPCMD);

  this->set_timeout(10, [this]() {
    uint8_t buffer = 0;

    // Read measurement
    bool read_status = this->read_byte(&buffer);

    if(read_status) {
      // Evaluate and publish measurements
      if(this->temp_sensor_ != nullptr) {
        // Temp data is one byte
        this->temp_sensor_->publish_state(buffer);
      }
    }
    else {
      ESP_LOGD(TAG, "Sensor temperature read failed");
    }
  });

  // Send humidity read command
  this->write_str(GETHUMCMD);

  this->set_timeout(10, [this]() {
    uint8_t buffer = 0;

    // Read measurement
    bool read_status = this->read_byte(&buffer);

    if(read_status) {
      if(this->humidity_sensor_ != nullptr) {
        // Relative humidity is one byte
        this->humidity_sensor_->publish_state(buffer);
      }
    }
    else {
      ESP_LOGD(TAG, "Sensor humidity read failed");
    }
  });
}

}  // namespace aq100
}  // namespace esphome