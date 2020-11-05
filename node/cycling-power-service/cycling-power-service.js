const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:cps');

const CyclingPowerMeasurementCharacteristic = require('./cycling-power-measurement-characteristic');
const CyclingPowerFeatureCharacteristic = require('./cycling-power-feature-characteristic');
const SensorLocationCharacteristic = require('./sensor-location-characteristic');

let CyclingPower = '1818'

// https://developer.bluetooth.org/gatt/services/Pages/ServiceViewer.aspx?u=org.bluetooth.service.cycling_power.xml
class CyclingPowerService extends bleno.PrimaryService {
  constructor() {
    trace('[CyclingPowerService] constructor');
    let cpmc = new CyclingPowerMeasurementCharacteristic();
    let cpfc = new CyclingPowerFeatureCharacteristic();
    let slc = new SensorLocationCharacteristic();
    super({
      uuid: CyclingPower,
      characteristics: [
        cpmc,
        cpfc,
        slc
      ]
    });

    this.cpmc = cpmc;
    this.cpfc = cpfc;
    this.slc = slc;
  }

  notify(event) {
    trace('[CyclingPowerService] notify')
    this.cpmc.notify(event);
    return this.RESULT_SUCCESS;
  };
}

module.exports = CyclingPowerService;
