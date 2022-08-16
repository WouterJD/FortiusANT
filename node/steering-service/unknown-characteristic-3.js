
const bleno = require('bleno');
const debug = require('debug');
const trace = debug('fortiusant:uc3');

const CharacteristicUserDescription = '2901';
const UnknownFeature3 = '347b0014-7635-408b-8918-8ff3949ce592';

class UnknownCharacteristic3 extends  bleno.Characteristic {
  constructor() {
    trace('[UnknownCharacteristic3] constructor');
    super({
      uuid: UnknownFeature3,
      properties: ['notify'],
      //descriptors: [
      //  new bleno.Descriptor({
      //    uuid: CharacteristicUserDescription,
      //    value: 'Unknown 3'
      //  })
      //],
    });

    this.updateValueCallback = null;
  }

  onSubscribe(maxValueSize, updateValueCallback) {
    trace('[UnknownCharacteristic3] onSubscribe');
    this.updateValueCallback = updateValueCallback;
    return this.RESULT_SUCCESS;
  };

  onUnsubscribe() {
    trace('[UnknownCharacteristic3] onUnsubscribe');
    this.updateValueCallback = null;
    return this.RESULT_UNLIKELY_ERROR;
  };
}

module.exports = UnknownCharacteristic3;
