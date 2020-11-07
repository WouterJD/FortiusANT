const bleno = require('bleno');

const HeartRateMeasurementCharacteristic = require('./heart-rate-measurement-characteristic');

const HeartRate = '180d';

class HeartRateService extends bleno.PrimaryService {
  constructor() {
    let hrmc = new HeartRateMeasurementCharacteristic();
    super({
      uuid: HeartRate,
      characteristics: [
        hrmc
      ]
    });

    this.hrmc = hrmc;
  }

  notify(event) {
    this.hrmc.notify(event);
    return this.RESULT_SUCCESS;
  };
}

module.exports = HeartRateService;
