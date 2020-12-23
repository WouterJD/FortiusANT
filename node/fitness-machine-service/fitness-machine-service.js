const bleno = require('bleno');
const debug = require('debug')('fortiusant:fms');

const FitnessMachineFeatureCharacteristic = require('./fitness-machine-feature-characteristic');
const IndoorBikeDataCharacteristic = require('./indoor-bike-data-characteristic');
const FitnessMachineControlPointCharacteristic = require('./fitness-machine-control-point-characteristic');
const SupportedPowerRangeCharacteristic = require('./supported-power-range-characteristic');

const FitnessMachine = '1826'

class FitnessMachineService extends bleno.PrimaryService {
  constructor(messages) {
    debug('[FitnessMachineService] constructor');
    let fmfc = new FitnessMachineFeatureCharacteristic();
    let ibdc = new IndoorBikeDataCharacteristic();
    let fmcpc = new FitnessMachineControlPointCharacteristic(messages);
    let sprc = new SupportedPowerRangeCharacteristic();
    super({
      uuid: FitnessMachine,
      characteristics: [
        fmfc,
        ibdc,
        fmcpc,
        sprc
      ]
    });

    this.fmfc = fmfc;
    this.ibdc = ibdc;
    this.fmcpc = fmcpc;
    this.sprc = sprc;
  }

  notify(event) {
    debug('[FitnessMachineService] notify')
    this.ibdc.notify(event);
    return this.RESULT_SUCCESS;
  };
}

module.exports = FitnessMachineService;
