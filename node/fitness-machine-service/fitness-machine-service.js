const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:fms');

const FitnessMachineFeatureCharacteristic = require('./fitness-machine-feature-characteristic');
const IndoorBikeDataCharacteristic = require('./indoor-bike-data-characteristic');

const FitnessMachine = '1826'

// TODO: do we need to advertise using Service Advertising Data??, or is this optional

class FitnessMachineService extends bleno.PrimaryService {
  constructor() {
    trace('[FitnessMachineService] constructor');
    let fmfc = new FitnessMachineFeatureCharacteristic();
    let ibdc = new IndoorBikeDataCharacteristic();
    super({
      uuid: FitnessMachine,
      characteristics: [
        fmfc,
        ibdc
      ]
    });

    this.fmfc = fmfc;
    this.ibdc = ibdc;
  }

  notify(event) {
    trace('[FitnessMachineService] notify')
    this.ibdc.notify(event);
    return this.RESULT_SUCCESS;
  };
}

module.exports = FitnessMachineService;
