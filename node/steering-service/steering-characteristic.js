const debug = require('debug')('fortiusant:sc');
const bleno = require('bleno');

const Steering = '347b0030-7635-408b-8918-8ff3949ce592';
const CharacteristicUserDescription = '2901';

class SteeringCharacteristic extends bleno.Characteristic {
  constructor() {
    super({
      uuid: Steering,
      properties: ['notify'],
      descriptors: [
        new bleno.Descriptor({
          uuid: CharacteristicUserDescription,
          value: 'Steering Angle'
        }),
      ]
    });
    this.updateValueCallback = null;  
  }

  onSubscribe(maxValueSize, updateValueCallback) {
    debug('[SteeringCharacteristic] onSubscribe');
    this.updateValueCallback = updateValueCallback;
    return this.RESULT_SUCCESS;
  };

  onUnsubscribe() {
    debug('[SteeringCharacteristic] onUnsubscribe');
    this.updateValueCallback = null;
    return this.RESULT_UNLIKELY_ERROR;
  };

  notify(event) {
    debug('[SteeringCharacteristic] notify');
    if ('steering_angle' in event) {
      let buffer = new Buffer.alloc(4);

      debug('[SteeringCharacteristic] Steering Angle(deg.): ' + event.steering_angle);

      buffer.writeFloatLE(event.steering_angle)

      if (this.updateValueCallback) {
        this.updateValueCallback(buffer);
      }
    }

    return this.RESULT_SUCCESS;
  }
};

module.exports = SteeringCharacteristic;
