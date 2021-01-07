const debug = require('debug')('fortiusant:hrm');
const bleno = require('bleno');

const HeartRateMeasurement = '2A37';
const CharacteristicUserDescription = '2901';

function bit(nr) {
  return (1 << nr);
}

const HeartRateValueFormat = bit(0);
const HeartRateValueFormatUint8 = 0;
const HeartRateValueFormatUint16 = HeartRateValueFormat;

class HeartRateMeasurementCharacteristic extends  bleno.Characteristic {
  constructor() {
    super({
      uuid: HeartRateMeasurement,
      properties: ['notify'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Heart Rate Measurement'
        })
      ]
    });
    this.updateValueCallback = null;  
  }

  onSubscribe(maxValueSize, updateValueCallback) {
    debug('[HeartRateMeasurementCharacteristic] onSubscribe');
    this.updateValueCallback = updateValueCallback;
    return this.RESULT_SUCCESS;
  };

  onUnsubscribe() {
    debug('[HeartRateMeasurementCharacteristic] onUnsubscribe');
    this.updateValueCallback = null;
    return this.RESULT_UNLIKELY_ERROR;
  };

  notify(event) {
    debug('[HeartRateMeasurementCharacteristic] notify');
    if ('heart_rate' in event) {
      let buffer = new Buffer.alloc(2);

      debug('[HeartRateMeasurementCharacteristic] heart rate(bpm): ' + event.heart_rate);

      buffer.writeUInt8(HeartRateValueFormatUint8, 0);
      buffer.writeUInt8(event.heart_rate, 1);

      if (this.updateValueCallback) {
        this.updateValueCallback(buffer);
      }
    }

    return this.RESULT_SUCCESS;
  }
};

module.exports = HeartRateMeasurementCharacteristic;
