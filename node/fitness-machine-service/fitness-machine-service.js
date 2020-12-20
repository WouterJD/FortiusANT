const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:fms');

const FitnessMachineFeatureCharacteristic = require('./fitness-machine-feature-characteristic');
const IndoorBikeDataCharacteristic = require('./indoor-bike-data-characteristic');
const FitnessMachineControlPointCharacteristic = require('./fitness-machine-control-point-characteristic');

const FitnessMachine = '1826'

class FitnessMachineService extends bleno.PrimaryService {
  constructor(messages) {
    trace('[FitnessMachineService] constructor');
    let fmfc = new FitnessMachineFeatureCharacteristic();
    let ibdc = new IndoorBikeDataCharacteristic();
    let fmcpc = new FitnessMachineControlPointCharacteristic(messages);
    super({
      uuid: FitnessMachine,
      characteristics: [
        fmfc,
        ibdc,
        fmcpc
      ]
    });

    this.fmfc = fmfc;
    this.ibdc = ibdc;
    this.fmcpc = fmcpc;
  }

  notify(event) {
    trace('[FitnessMachineService] notify')
    this.ibdc.notify(event);
    return this.RESULT_SUCCESS;
  };
}

module.exports = FitnessMachineService;
